```mermaid
sequenceDiagram
    participant User
    participant Script
    participant AzureAPI
    participant DataProcessor
    participant HighImpactChecker
    participant AzureML
    participant WeightCalculator
    participant Scheduler

    User ->> Script: Start Execution
    Script ->> AzureAPI: Retrieve System Metrics
    AzureAPI -->> Script: System Metrics Data
    Script ->> DataProcessor: Preprocess Data
    DataProcessor -->> Script: Preprocessed Data
    Script ->> HighImpactChecker: Check for High Impact Users
    HighImpactChecker -->> Script: High Impact Users Data
    Script ->> AzureML: Predict Deployment Groups
    AzureML -->> Script: Deployment Group Predictions
    Script ->> WeightCalculator: Calculate Weights for Rings
    WeightCalculator -->> Script: 20% Weight for Each Ring
    Script ->> Scheduler: Divide Systems into 8 Rings with Calculated Weights
    Scheduler -->> Script: Deployment Rings
    Script ->> Scheduler: Schedule Patches/Deployments
    Scheduler -->> Script: Patching/Deployment Schedule
    Script -->> User: Deployment schedule created successfully!
