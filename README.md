```mermaid
flowchart TD
    A[User Input]
    B[PowerShell Script Execution]
    C[Retrieve System Metrics/API]
    D[Data Preprocessing]
    E[Check for High Impacted Users]
    F[Identify High Impact Users]
    G[Azure ML Model]
    H[Train/Predict Deployment Groups]
    I[Divide Systems into 8 Deployment Rings]
    J[Schedule Patches/Deployments]

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
