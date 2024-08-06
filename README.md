```mermaid
flowchart TD
    A[User Input]
    B[Script Execution]
    C[Retrieve System Metrics/API]
    D[Data Preprocessing]
    E[Check for High Impacted Users]
    F[Identify High Impact Users]
    G[Azure ML Model]
    H[Train/Predict Deployment Groups]
    I[Calculate Weight for Each Ring]
    J[20% Weight per Ring Calculation]
    K[Divide Systems into 8 Deployment Rings with Calculated Weights]
    L[Schedule Patches/Deployments]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    D --> G
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
