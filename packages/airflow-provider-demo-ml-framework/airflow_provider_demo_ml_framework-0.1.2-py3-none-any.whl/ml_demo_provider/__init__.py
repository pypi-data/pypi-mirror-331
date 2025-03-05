def get_provider_info():
    return {
        "package-name": "airflow-provider-demo-ml-framework",
        "name": "DEMO ML Framework Airflow Provider",
        "description": "DEMO ML Framework Airflow provider.",
        "versions": ["0.1.2"],
        "connection-types": [
            {
                "hook-class-name": "ml_demo_provider.hooks.ml_demo_framework.DatasetStorageHook",
                "connection-type": "http",
            },
        ],
        "extra-links": [],
    }
