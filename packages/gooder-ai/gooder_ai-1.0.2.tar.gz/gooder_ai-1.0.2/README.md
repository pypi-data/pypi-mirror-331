# Gooder AI Package

The `gooder_ai` Python package provides a seamless way to visualize model data by combining JSON configurations and Pandas DataFrames. It opens the [Gooder.ai](https://latest.gooder.ai) visualization tool, allowing users to interactively analyze their model performance.

## Features
- Accepts JSON and Pandas DataFrame as inputs.
- Automatically opens the [Gooder.ai](https://latest.gooder.ai) tool for visualization.
- Simplifies the process of visualizing complex model data and validating ML models.

## Installation
Install the package using pip:

```bash
pip install gooder_ai
```

## Usage
Here's an example of how to use the `valuate_model` function:

```python
from gooder_ai import valuate_model
import pandas as pd

# Example Pandas DataFrame
data = pd.DataFrame({
    "feature1": [1, 2, 3, 4],
    "feature2": [5, 6, 7, 8]
})

# Visualize the model
await valuate_model(
    email="test@gmail.com",  # required
    password="test@123",  # required
    data=data,  # required
    config=config,  # required gooder config.
    mode=mode,  # required possible values can be public | private | protected.
    view_id=view_id,  # Optional
    dataset_name="dataset", # Optional

    # AWS Configuration
    api_url="api_url",  # Optional
    app_client_id="app_client_id",  # Optional
    identity_pool_id="identity_pool_id",  # Optional
    user_pool_id="user_pool_id",  # Optional
    bucket_name="bucket_name",  # Optional
    base_url="base_url"  # Optional
)
```

## Function Parameters

### `valuate_model(**kwargs)`
- email (str): User's email for authentication.
- password (str): User's password for authentication.
- data (DataFrame): Data to be uploaded.
- config (dict): Configuration dictionary for the upload.
- mode (Literal["public", "protected", "private"]): Mode of the view.
- dataset_name (str | None): Name of dataset, if any.
- view_id (str | None): ID of the view to update, if any.
- api_url (str | None): GraphQL API URL.
- app_client_id (str | None): Client ID for an app in a Cognito User Pool.
- identity_pool_id (str | None): ID for an Amazon Cognito Identity Pool.
- user_pool_id (str | None): ID for the Cognito User Pool that manages user authentication.
- bucket_name (str | None): S3 bucket name storing datasets and configs.
- base_url (str | None): Gooder app URL.

## Config

# Chart Definition Configuration Example

Given below is an example chart/dashboard configuration for the Gooder AI app:

```typescript
const config = {
  "activeFilter": null, // Optional: ID of the active filter (default: null)
  "customChartLayoutMap": {
    "xl": [ // Layout for extra-large screens
      {
        "i": "d292c59c-e1f6-4f7e-ac53-525b7b6e6a56", // Chart ID
        "x": 0, // X position (grid units)
        "y": 0, // Y position (grid units)
        "w": 11, // Width (grid units)
        "h": 9, // Height (grid units)
        "moved": false, // Optional: Whether the item has been moved (default: false)
        "static": false // Optional: Whether the item is static (default: false)
      },
      // ... other xl layouts
    ],
    "lg": [ // Layout for large screens
      // ... similar structure as xl
    ],
    "md": [ // Layout for medium screens
      // ... similar structure as xl
    ],
    "sm": [ // Layout for small screens
      {
        "i": "2db67e79-3c40-40c5-ae42-7d426fa37597", // Chart ID
        "x": 0,
        "y": 36,
        "w": 12,
        "h": 12
      }
    ],
    "xs": [ // Layout for extra-small screens
      // ... similar structure as sm
    ]
  },
  "customCharts": [
    {
      "id": "74a92600-9334-4e57-afe5-2dbb61526547", // Required: Unique chart ID (UUID)
      "dataInitializationCode": "data init script", // Required: Script to initialize chart data
      "metricCalculationCode": "data calculate script", // Required: Script to calculate metrics
      "metric": "Num responses", // Required: Metric name (displayed on Y-axis)
      "title": "Response deciles", // Optional: Chart title (default: null)
      "resolution": 10, // Required: Number of data points/bins
      "unit": "none", // Required: Y-axis unit (from UnitTypes enum)
      "decimalPlaces": 2, // Optional: Decimal precision (default: 2)
      "minRange": 0, // Required: Minimum zoom range (0-100)
      "maxRange": 100, // Required: Maximum zoom range (0-100)
      "seriesType": "bar", // Required: Chart type (line/bar from SeriesTypes)
      "showRangeSlider": false, // Optional: Shows zoom slider on dashboard (default: false)
      "showInDashboard": true, // Required: Display chart on dashboard
      "showInMetricTable": true, // Required: Show metric in the table
      "showBaseline": false, // Optional: Display baseline (default: false)
      "description": null, // Optional: Chart description (default: null)
      "aspectRatio": null, // Optional: Aspect ratio (default: null)
      "scaleMetric": true, // Optional: Scale Y-axis with projected population (default: true)
      "suppressBar": true, // Optional: Hide the first bar for bar series (default: false)
      "suppressXAxisLabel": true, // Optional: Hide X-axis labels (default: false)
      "showThreshold": true, // Optional: Show threshold line (default: false)
      "reverseXAxis": false, // Optional: Reverse X-axis for bar series (default: false)
      "aiPrompt": null, // Optional: Custom AI prompt (default: null)
      "highlightType": "none", // Optional: Highlight type (from HighlightType, default: "none")
      "optimizeResolution": false // Optional: Optimize resolution (default: true)
    }
  ],
  "datasetID": "", // Optional: Dataset ID (format: dataset_name/Sheet1)
  "dependentVariable": "TARGET", // Required: Dependent variable column name
  "filters": null, // Optional: Array of rule IDs (default: null)
  "isOffline": false, // Optional: Offline mode toggle (default: false)
  "numberOfRowsSentInAIPrompt": 10, // Optional: Rows sent to AI (default: 10)
  "percentTreated": null, // Optional: Current % treated value (default: null)
  "positivePolarityValues": ["1"], // Required: Positive values of dependent variable
  "projectedPopulation": null, // Optional: Population scaling value (default: null)
  "rules": [ // Optional: Array of rules (default: null)
    {
      "id": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Rule ID (UUID)
      "value": "abcd", // Required: Value (string/number/boolean/array)
      "operator": ">" // Required: Operator (from Operators enum)
    }
  ],
  "scores": [
    {
      "fieldName": "P (TARGET=1) Min", // Required: Model field name
      "fieldLabel": "Model 3", // Optional: Display name (default: fieldName)
      "sortOrder": "desc" // Optional: Sorting (asc/desc, default: "desc")
    }
  ],
  "showFiltersOnDashboard": false, // Optional: Show filter controls (default: false)
  "sliderAssociations": [
    {
      "sliderID": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Slider ID
      "uswID": "d292c59c-e1f6-4f7e-ac53-525b7b6e6a56", // Required: Chart ID
      "showInDashboard": false // Optional: Show slider on dashboard (default: false)
    }
  ],
  "sliders": [
    {
      "id": "29a827d4-35ac-410e-9a31-45203dc1bb18", // Required: Slider ID (UUID)
      "name": "Cost of contact", // Required: Slider name
      "description": null, // Optional: Description (default: null)
      "min": 0, // Required: Minimum value
      "max": 100, // Required: Maximum value
      "value": 10, // Required: Current value
      "label": "coc" // Optional: Display label (default: null)
    }
  ],
  "title": "Targeted Marketing", // Optional: Dashboard title (default: null)
  "variableSelectors": null, // Optional: Variable aliases (default: null)
  "version": "2.3", // Optional: Config version (latest: 2.3, default: 1.0)
  "xAxisName": "Percent treated" // Optional: X-axis label (default: "Percent treated")
};
```