#define TIME   100
#define SPEED  700

// B = Back face motor  (X axis on RAMPS)
#define B_STEP 54
#define B_DIR  55
#define B_EN   38

// R = Right face motor   (Y axis on RAMPS)
#define R_STEP 60
#define R_DIR  61
#define R_EN   56

// D = Down face motor     (Z axis on RAMPS)
#define D_STEP 46
#define D_DIR  48
#define D_EN   62

// L = Left face motor   (E0 axis on RAMPS)
#define L_STEP 26
#define L_DIR  28
#define L_EN   24

// F = Front face motor  (E1 axis on RAMPS)
#define F_STEP 36
#define F_DIR  34
#define F_EN   30


#define STEPS_PER_REV  200 
int steps90  = (STEPS_PER_REV * 1) / 4;
int steps180 = (STEPS_PER_REV * 2) / 4;
int stepi90  = (STEPS_PER_REV * 3) / 4;

String solution = "";       // Holds incoming serial data
bool received = false;   // Goes true when '\n' is received
bool scramble = false; // Flag to determine mode

void setup() 
{
  Serial.begin(115200);

  pinMode(F_EN, OUTPUT);  pinMode(F_STEP, OUTPUT);  pinMode(F_DIR, OUTPUT);
  pinMode(B_EN, OUTPUT);  pinMode(B_STEP, OUTPUT);  pinMode(B_DIR, OUTPUT);
  pinMode(L_EN, OUTPUT);  pinMode(L_STEP, OUTPUT);  pinMode(L_DIR, OUTPUT);
  pinMode(D_EN, OUTPUT);  pinMode(D_STEP, OUTPUT);  pinMode(D_DIR, OUTPUT);
  pinMode(R_EN, OUTPUT);  pinMode(R_STEP, OUTPUT);  pinMode(R_DIR, OUTPUT);
  
  digitalWrite(F_EN, HIGH);
  digitalWrite(B_EN, HIGH);
  digitalWrite(L_EN, HIGH);
  digitalWrite(D_EN, HIGH);
  digitalWrite(R_EN, HIGH);

  Serial.println("Rubik's Cube Solver Ready!");

  solution.reserve(200);   // Reserve memory for input
}

void loop() 
{
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read();
    if (inChar == '\n') 
    {
      received = true;
    } else 
    {
      solution += inChar;
    }
  }

  if (received) 
  {
    solution.trim();
    
    // Check if it's a scramble command
    if (solution.endsWith("S")) 
    {
      scramble = true;
      solution.remove(solution.length() - 1); // Remove the 'S'
    } else 
    {
      scramble = false;
    }

    solution += " ";  // Trailing space so last move is caught

    if (!scramble) 
    {
      Serial.println("Received: " + solution);
    }

    while (solution.length() > 0) 
    {
      int spaceIndex = solution.indexOf(' ');
      String move = solution.substring(0, spaceIndex);
      if (move.length() > 0) {
        executeMove(move, scramble);
      }
      solution = solution.substring(spaceIndex + 1);
    }

    if (scramble) 
    {
      Serial.println("Scrambling done.");
    } else {
      Serial.println("→ Operation Completed.");
    }
    
    Serial.println("=======================================");
    Serial.println();
    Serial.println("Rubik's Cube Solver Ready!");

    solution = "";
    received = false;
  }
}

void executeMove(String move, bool silent) 
{
  if (!silent) 
  {
    Serial.print("→ Executing move: ");
    Serial.print(move);
  }

  int steps = steps90;
  bool clockwise = true;

  char face = move.charAt(0);

  if (move.endsWith("2")) 
  {
    steps = steps180;
    clockwise = true;
  } 
  else if (move.endsWith("'")) 
  {
    steps = stepi90;
    clockwise = true;
  }

  switch (face) 
  {
    case 'F':
      rotateFace(F_EN, F_STEP, F_DIR, steps, clockwise);
      digitalWrite(F_EN, HIGH);
      break;
    case 'B':
      rotateFace(B_EN, B_STEP, B_DIR, steps, clockwise);
      digitalWrite(B_EN, HIGH);
      break;
    case 'L':
      rotateFace(L_EN, L_STEP, L_DIR, steps, clockwise);
      digitalWrite(L_EN, HIGH);
      break;
    case 'D':
      rotateFace(D_EN, D_STEP, D_DIR, steps, clockwise);
      digitalWrite(D_EN, HIGH);
      break;
    case 'R':
      rotateFace(R_EN, R_STEP, R_DIR, steps, clockwise);
      digitalWrite(R_EN, HIGH);
      break;
    default:
      if (!silent) Serial.print(" [UNKNOWN MOVE - skipped]");
      break;
  }

  if (!silent) Serial.println(" Done.");
  delay(TIME);
}

void rotateFace(int enPin, int stepPin, int dirPin, int steps, bool clockwise) 
{
  digitalWrite(dirPin, clockwise ? LOW : HIGH);
  digitalWrite(enPin, LOW);
  delayMicroseconds(TIME);

  for (int i = 0; i < steps; i++) 
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(SPEED);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(SPEED);
  }
}