# Airflow Custom Deferrable Dataflow Operator
**Trigger Different: Cut Your AirFlow Costs By Starting From Triggerer!**

Use this simple Airflow Operator to start your Dataflow jobs execution directly from the Triggerer without going to the Worker!

# Contents

- [How it works](#how)
- [Installation](#installation)
- [Usage](#usage)
- [Contribute](#contribute)

# How It Works <a id="how"></a>
The main idea of this approach is to start the task instance execution [directly on the Triggerer](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html#triggering-deferral-from-task-start) component, bypassing the worker entirely.

This strategy is effective because, in this case, the only action the operator performs is making an HTTP request to start the external processing service and waiting for the job to complete.

For this reason, we can leverage the async design of the Triggerer for this execution, significantly reducing resource consumption. By using this architecture, the Airflow task execution proccess will be something like the following:

![airflow_diagram](assets/airflow_diagram.png)

To know more about how the tool works, check out the Medium article.

# Installation <a id="installation"></a>
The installation process will depend on your cloud provider or how you have set up your environment. 

Regarding [Google Cloud Composer](https://cloud.google.com/composer?hl=en), for example, the **DAGs folder** is not synchronized with the Airflow Triggerer, as stated in the [documentation](https://cloud.google.com/composer/docs/composer-2/troubleshooting-triggerer#trigger_class_not_found). 

Consequently, just uploading your code to the DAGs folder will not work, and you'll likely face an error like this: ```ImportError: Module "PACKAGE_NAME" does not define a "CLASS_NAME" attribute/class```

In this case, it's necessary to [import the missing code from PyPI](https://cloud.google.com/composer/docs/composer-2/install-python-dependencies), meaning that you'll need to install the operator/trigger as a new library.

To do so, you can use the following command:

```bash
pip install custom-deferrable-dataflow-operator
```

# Usage <a id="usage"></a>
After installing the library, you can successfully import and use the operator in your Airflow DAGs, as shown below:

```python
from deferrable_dataflow_operator import DeferrableDataflowOperator

dataflow_triggerer_job = DeferrableDataflowOperator(
    trigger_kwargs={
        "project_id": GCP_PROJECT_ID,
        "region": GCP_REGION,
        "body": {
            "job_name": MY_JOB_NAME,
            "parameters": {
                "dataflow-parameters": MY_PARAMETERS
            },
            "environment": {**dataflow_env_vars},
            "container_spec_gcs_path": TEMPLATE_GCS_PATH,
        }
    },
    start_from_trigger=True,
    task_id=MY_TASK_ID
)
```
In the ```trigger_kwargs``` parameter, it's important to specify your GCP project ID and region. The ```body``` parameter, on the other hand, should contain all the relevant information for your Dataflow job, as stated in the [official documentation](https://cloud.google.com/python/docs/reference/dataflow/latest/google.cloud.dataflow_v1beta3.types.LaunchFlexTemplateParameter).

# Contributing <a id="contribute"></a>
This project is open to contributions! If you want to collaborate to improve the operator, please follow these steps:

1.  Open a new issue to discuss the feature or bug you want to address.
2.  Once approved, fork the repository and create a new branch.
3.  Implement the changes.
4.  Create a pull request with a detailed description of the changes.
