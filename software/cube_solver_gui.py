import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import threading
import time
import kociemba
import serial
import cv2
import numpy as np
from PIL import Image, ImageTk

color_map = {
    'W': 'white', 'Y': 'yellow', 'G': 'green',
    'B': 'blue', 'R': 'red', 'O': 'orange'
}

cube_face_mapping = {
    'W': 'U', 'Y': 'D', 'R': 'F', 'B': 'R', 'O': 'B', 'G': 'L'
}

face_order = ['U', 'D', 'L', 'R', 'F', 'B']

face_center_color = {
    'U': 'W', 'D': 'Y', 'L': 'G', 'R': 'B', 'F': 'R', 'B': 'O'
}

default_colors = {
    'U': 'WWW\nWWW\nWWW',
    'D': 'YYY\nYYY\nYYY',
    'L': 'GGG\nGGG\nGGG',
    'R': 'BBB\nBBB\nBBB',
    'F': 'RRR\nRRR\nRRR',
    'B': 'OOO\nOOO\nOOO'
}


class CubeSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Rubik's Cube Solver")
        self.text_boxes = {}
        self.face_previews = {}
        self.moves = []
        self.serial_port_obj = None
        self.serial_thread = None
        self.serial_thread_running = False
        self.cap = None
        self.calibration_values = {}

        self.calibrated = False
        self.current_calib_idx = 0
        self.calib_order = ['W', 'Y', 'G', 'B', 'R', 'O']

        self.current_face_idx = 0
        self.temp_detected_face = ""
        self.camera_active = False
        self.camera_mode = None

        left_col = tk.Frame(root)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)

        right_col = tk.Frame(root)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        top_frame = tk.Frame(left_col)
        top_frame.pack(pady=10, fill=tk.X)
        tk.Label(top_frame, text="Arduino Rubik's Cube Solver", font=("Roboto", 16)).pack(pady=5)

        port_frame = tk.Frame(top_frame)
        port_frame.pack(pady=5)
        tk.Label(port_frame, text="Select Port:").pack(side=tk.LEFT, padx=5)
        self.combobox = ttk.Combobox(port_frame, values=self.get_serial_ports(), width=15)
        self.combobox.pack(side=tk.LEFT, padx=5)
        tk.Button(port_frame, text="Refresh", command=self.refresh_ports).pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(left_col)
        main_frame.pack(padx=20, pady=10)
        for row, face in enumerate(face_order):
            tk.Label(main_frame, text=f"{face} Face").grid(row=row * 2, column=0, sticky='s', pady=(5, 0))
            tk.Label(main_frame, text=f"{face} Preview").grid(row=row * 2, column=1, sticky='s', pady=(5, 0))
            tb = tk.Text(main_frame, width=6, height=3, font=("Courier", 14), wrap='none')
            tb.insert(tk.END, default_colors[face])
            tb.grid(row=row * 2 + 1, column=0, padx=10, pady=5)
            self.text_boxes[face] = tb
            preview_frame = tk.Frame(main_frame)
            preview_frame.grid(row=row * 2 + 1, column=1, padx=10, pady=5)
            self.face_previews[face] = preview_frame

        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=len(face_order) * 2, column=0, columnspan=2, pady=15)
        tk.Button(btn_frame, text="Generate Cube", command=self.generate_cube, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Scramble", command=self.scramble_cube_serial, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Solve", command=self.solve_cube_serial, width=15).pack(side=tk.LEFT, padx=10)

        self.solution_label = tk.Label(main_frame, text="", font=("Courier", 12))
        self.solution_label.grid(row=len(face_order) * 2 + 1, column=0, columnspan=2, pady=5)

        right_col.grid_rowconfigure(0, weight=1, uniform="group1")
        right_col.grid_rowconfigure(1, weight=1, uniform="group1")
        right_col.grid_columnconfigure(0, weight=1)

        camera_section = tk.Frame(right_col)
        camera_section.grid(row=0, column=0, sticky='nsew', pady=(0, 5))

        tk.Label(camera_section, text="Camera Feed", font=("Helvetica", 11, "bold")).pack(anchor='w')

        cam_btn_frame = tk.Frame(camera_section)
        cam_btn_frame.pack(fill=tk.X, pady=3)
        tk.Button(cam_btn_frame, text="Calibrate", command=self.start_calibration_inline).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(cam_btn_frame, text="Capture", command=self.start_capture_inline).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(cam_btn_frame, text="Stop Camera", command=self.hide_camera_ui, fg="red").pack(side=tk.LEFT)

        self.cam_info_label = tk.Label(camera_section, text="Camera is off", font=("Helvetica", 10, "bold"), fg="gray")
        self.cam_info_label.pack(anchor='w', pady=(2, 2))

        self.cam_action_btn = tk.Button(camera_section, text="Next", width=15, command=self.camera_action)

        self.cam_monitor_frame = tk.Frame(camera_section, bg='black')
        self.cam_monitor_frame.pack(fill=tk.BOTH, expand=True)

        self.cam_off_label = tk.Label(self.cam_monitor_frame, text="[ Camera Off ]", bg='black', fg='gray',
                                      font=("Courier", 12))
        self.cam_off_label.place(relx=0.5, rely=0.5, anchor='center')

        self.cam_feed_label = tk.Label(self.cam_monitor_frame, bg='black')
        self.cam_feed_label.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.cam_feed_label.lower()

        self.setup_serial_monitor_grid(right_col)
        self.generate_cube()

    def setup_serial_monitor_grid(self, parent_frame):
        monitor_section = tk.Frame(parent_frame)
        monitor_section.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        label_frame = tk.Frame(monitor_section)
        label_frame.pack(anchor='w', fill=tk.X)
        tk.Label(label_frame, text="Serial Monitor", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)
        tk.Button(label_frame, text="Clear", command=self.clear_serial_monitor, width=6).pack(side=tk.LEFT, padx=10)
        text_frame = tk.Frame(monitor_section)
        text_frame.pack(fill=tk.BOTH, expand=True)
        self.serial_monitor = tk.Text(text_frame, state='disabled', bg='black', fg='lime', font=("Courier", 10))
        self.serial_monitor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame, command=self.serial_monitor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.serial_monitor['yscrollcommand'] = scrollbar.set

    def refresh_ports(self):
        self.combobox['values'] = self.get_serial_ports()
        self.combobox.set('')

    def get_serial_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def clear_serial_monitor(self):
        self.serial_monitor['state'] = 'normal'
        self.serial_monitor.delete('1.0', tk.END)
        self.serial_monitor['state'] = 'disabled'

    def start_serial_monitor_thread(self, port):
        if self.serial_thread_running: return
        try:
            self.serial_port_obj = serial.Serial(port, 115200, timeout=0.5)
            self.serial_thread_running = True
            self.serial_thread = threading.Thread(target=self.serial_read_thread, daemon=True)
            self.serial_thread.start()
            self.append_serial_monitor(f"--- Serial monitor started on {port} ---\n")
        except Exception as e:
            self.append_serial_monitor(f"Error: {e}\n")

    def stop_serial_monitor_thread(self):
        self.serial_thread_running = False
        if self.serial_port_obj and self.serial_port_obj.is_open:
            self.serial_port_obj.close()
            self.append_serial_monitor("--- Serial monitor stopped ---\n")

    def serial_read_thread(self):
        while self.serial_thread_running:
            try:
                if self.serial_port_obj.in_waiting > 0:
                    data = self.serial_port_obj.readline().decode(errors='ignore').strip()
                    if data: self.append_serial_monitor(f"Arduino -> {data}\n")
                else:
                    time.sleep(0.1)
            except:
                self.serial_thread_running = False

    def append_serial_monitor(self, text):
        def inner():
            self.serial_monitor['state'] = 'normal'
            self.serial_monitor.insert(tk.END, text)
            self.serial_monitor.see(tk.END)
            self.serial_monitor['state'] = 'disabled'
        self.root.after(0, inner)

    def generate_cube(self):
        for preview in self.face_previews.values():
            for widget in preview.winfo_children(): widget.destroy()
        for face in face_order:
            text = self.text_boxes[face].get("1.0", tk.END).strip().replace('\n', '').upper()
            if len(text) != 9 or any(c not in color_map for c in text): continue
            self.draw_face(self.face_previews[face], text)

    def draw_face(self, frame, face_str):
        for i in range(3):
            row_frame = tk.Frame(frame)
            row_frame.pack()
            for j in range(3):
                letter = face_str[i * 3 + j].upper()
                color = color_map.get(letter, 'gray')
                tk.Label(row_frame, bg=color, width=3, height=1, relief='solid', borderwidth=1).pack(side=tk.LEFT, padx=1, pady=1)

    def build_cube_string(self):
        faces = {}
        for face in face_order:
            text = self.text_boxes[face].get("1.0", tk.END).strip().replace('\n', '').upper()
            if len(text) != 9:
                return None, f"Face {face} must have exactly 9 characters."
            if any(c not in color_map for c in text):
                return None, f"Face {face} contains invalid characters."
            faces[face] = [cube_face_mapping[c] for c in text]
        cube_string = ''.join(''.join(faces[f]) for f in ['U', 'R', 'F', 'D', 'L', 'B'])
        return cube_string, None

    def parse_solution(self, raw_result):
        solution = raw_result.strip()
        if "(" in solution:
            solution = solution.split("(")[0].strip()

        solution = solution.replace("3", "'").replace("1", "")
        solution = solution.replace("U2", "R L' F2 B2 R L' D L R' B2 F2 L R' R L' F2 B2 R L' D L R' B2 F2 L R'").replace("U'", "R L' F2 B2 R L' D' L R' B2 F2 L R'").replace("U", "R L' F2 B2 R L' D L R' B2 F2 L R'")

        moves = solution.split()
        return moves

    def solve_cube_serial(self):
        cube_string, err = self.build_cube_string()
        if err:
            messagebox.showerror("Error", err)
            return

        if cube_string == 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB':
            messagebox.showinfo("Already Solved", "The Cube Is Already Solved!")
            return

        try:
            raw_result = kociemba.solve(cube_string)
        except Exception as e:
            messagebox.showerror("Error", "Wrong Cube Faces!")
            return

        self.moves = self.parse_solution(raw_result)
        self.solution_label.config(text=f"Solution: {len(self.moves)} moves", fg="blue")

        port = self.combobox.get()
        if port:
            threading.Thread(target=self.send_moves_serial, daemon=True).start()
        else:
            messagebox.showwarning("No Port Selected", "Please Select a COM Port.")

    def scramble_cube_serial(self):
        cube_string, err = self.build_cube_string()
        if err:
            messagebox.showerror("Error", err)
            return

        try:
            raw_result = kociemba.solve(cube_string)
        except Exception as e:
            messagebox.showerror("Error", "Wrong Cube Faces!")
            return

        if cube_string == 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB':
            messagebox.showinfo("Nothing to Scramble", "Nothing to Scramble!")
            return

        solution_moves = self.parse_solution(raw_result)

        if not solution_moves:
            messagebox.showinfo("Nothing to Scramble", "Nothing to Scramble!")
            return

        solution_moves.reverse()

        scramble_moves = []
        for move in solution_moves:
            if move.endswith("2"):
                scramble_moves.append(move)
            elif move.endswith("'"):
                scramble_moves.append(move[:-1])
            else:
                scramble_moves.append(move + "'")

        scramble_moves.append("S")
        self.moves = scramble_moves
        self.solution_label.config(text=f"Scramble: {len(self.moves) - 1} moves", fg="orange")

        port = self.combobox.get()
        if port:
            threading.Thread(target=self.send_moves_serial, daemon=True).start()
        else:
            messagebox.showwarning("No Port Selected", "Please Select a COM Port.")

    def send_moves_serial(self):
        port = self.combobox.get()
        if not port:
            return
        if not self.serial_thread_running:
            self.start_serial_monitor_thread(port)
        try:
            time.sleep(4)
            cmd = ' '.join(self.moves) + '\n'
            self.serial_port_obj.write(cmd.encode('utf-8'))
            self.append_serial_monitor(f"PC -> {cmd}")
        except Exception as e:
            messagebox.showerror("Serial Error", str(e))

    def show_camera_ui(self):
        self.cam_off_label.place_forget()
        self.cam_feed_label.lift()
        self.cam_action_btn.pack(after=self.cam_info_label, pady=(0, 4))

    def hide_camera_ui(self):
        self.cam_feed_label.lower()
        self.cam_feed_label.configure(image='')
        self.cam_off_label.place(relx=0.5, rely=0.5, anchor='center')
        self.cam_action_btn.pack_forget()
        self.cam_info_label.config(text="Camera is off", fg="gray")
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_active = False

    def camera_action(self):
        if self.camera_mode == 'calibrate':
            self.next_calibration_step()
        elif self.camera_mode == 'capture':
            self.next_capture_step()

    def start_calibration_inline(self):
        self.current_calib_idx = 0
        self.camera_mode = 'calibrate'
        self.camera_active = True
        self.cap = cv2.VideoCapture(0)
        self.cam_action_btn.config(text="Capture Color")
        self.show_camera_ui()
        self.update_camera_loop()

    def start_capture_inline(self):
        if not self.calibrated:
            messagebox.showinfo("Setup", "Calibration is required!")
            self.start_calibration_inline()
            return

        self.current_face_idx = 0
        self.camera_mode = 'capture'
        self.camera_active = True
        self.cap = cv2.VideoCapture(0)
        self.cam_action_btn.config(text="Next Face")
        self.show_camera_ui()
        self.update_camera_loop()

    def update_camera_loop(self):
        if not self.camera_active or not self.cap: return
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            size = 330

            if self.camera_mode == 'calibrate':
                x1, y1 = w // 2 - size // 2, h // 2 - size // 2
                x2, y2 = x1 + size, y1 + size
                target = self.calib_order[self.current_calib_idx]
                self.cam_info_label.config(text=f"Calibrating: {target}", fg="darkblue")
                roi = frame[y1:y2, x1:x2]
                self.last_hsv_captured = np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).reshape(-1, 3), axis=0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, target, (x1 + 100, y1 + 200), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 4)

            elif self.camera_mode == 'capture':
                start_x, start_y = w // 2 - size // 2, h // 2 - size // 2
                step = size // 3
                face_key = face_order[self.current_face_idx]
                center_color = face_center_color[face_key]
                self.cam_info_label.config(text=f"Scanning Face: {face_key} (Center: {center_color})", fg="darkblue")

                det_list = []
                for i in range(3):
                    for j in range(3):
                        x1, y1 = start_x + j * step, start_y + i * step
                        x2, y2 = x1 + step, y1 + step

                        if i == 1 and j == 1:
                            best_col = center_color
                        else:
                            roi = frame[y1 + 15:y2 - 15, x1 + 15:x2 - 15]
                            if roi.size > 0:
                                hsv = np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).reshape(-1, 3), axis=0)
                                best_col = 'W'
                                min_d = float('inf')
                                for c, val in self.calibration_values.items():
                                    dh = min(abs(hsv[0] - val[0]), 180 - abs(hsv[0] - val[0])) * 3.5
                                    ds = abs(hsv[1] - val[1]) * 1.5
                                    dv = abs(hsv[2] - val[2]) * 0.5
                                    d = dh + ds + dv
                                    if d < min_d: min_d, best_col = d, c
                            else:
                                best_col = 'W'

                        det_list.append(best_col)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                        cv2.putText(frame, best_col, (x1 + 30, y1 + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                row1 = det_list[0:3][::-1]
                row2 = det_list[3:6][::-1]
                row3 = det_list[6:9][::-1]
                self.temp_detected_face = "".join(row1 + row2 + row3)

            fw, fh = self.cam_monitor_frame.winfo_width(), self.cam_monitor_frame.winfo_height()
            if fw > 10:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((fw, fh))
                imgtk = ImageTk.PhotoImage(image=img)
                self.cam_feed_label.imgtk = imgtk
                self.cam_feed_label.configure(image=imgtk)

        self.root.after(10, self.update_camera_loop)

    def next_calibration_step(self):
        self.calibration_values[self.calib_order[self.current_calib_idx]] = self.last_hsv_captured
        self.current_calib_idx += 1
        if self.current_calib_idx >= len(self.calib_order):
            self.calibrated = True
            self.hide_camera_ui()
            messagebox.showinfo("Success", "Calibration Complete!")

    def next_capture_step(self):
        face_key = face_order[self.current_face_idx]
        fmt = "\n".join([self.temp_detected_face[i * 3:(i + 1) * 3] for i in range(3)])
        self.text_boxes[face_key].delete("1.0", tk.END)
        self.text_boxes[face_key].insert(tk.END, fmt)
        self.generate_cube()
        self.current_face_idx += 1
        if self.current_face_idx >= len(face_order):
            self.hide_camera_ui()
            messagebox.showinfo("Success", "All faces scanned!")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x850")
    app = CubeSolverGUI(root)
    root.mainloop()