# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from airflow import DAG
from airflow.contrib.operators import gcs_to_bq, kubernetes_pod_operator

default_args = {
    "owner": "Google",
    "depends_on_past": False,
    "start_date": "2021-03-01",
}


with DAG(
    dag_id="race_and_economic_opportunity.national_child_and_parent_income_transition_matrices_by_race_and_gender",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@daily",
    catchup=False,
    default_view="graph",
) as dag:

    # Run CSV transform within kubernetes pod
    income_transition_transform_csv = kubernetes_pod_operator.KubernetesPodOperator(
        task_id="income_transition_transform_csv",
        startup_timeout_seconds=600,
        name="race_and_economic_opportunity_national_child_and_parent_income_transition_matrices_by_race_and_gender",
        namespace="default",
        affinity={
            "nodeAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [
                        {
                            "matchExpressions": [
                                {
                                    "key": "cloud.google.com/gke-nodepool",
                                    "operator": "In",
                                    "values": ["pool-e2-standard-4"],
                                }
                            ]
                        }
                    ]
                }
            }
        },
        image_pull_policy="Always",
        image="{{ var.json.race_and_economic_opportunity.container_registry.run_csv_transform_kub }}",
        env_vars={
            "SOURCE_URL": "https://www2.census.gov/ces/opportunity/table_2-3.csv",
            "SOURCE_FILE": "files/data.csv",
            "TARGET_FILE": "files/data_output.csv",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/race_and_economic_opportunity/national_child_and_parent_income_transition_matrices_by_race_and_gender/data_output.csv",
            "CSV_HEADERS": '["kid_race","gender","count","kir_q1","kir_q2","kir_q3","kir_q4","kir_q5","kfr_q1","kfr_q2","kfr_q3","kfr_q4","kfr_q5","par_q1","par_q2","par_q3","par_q4","par_q5","kir_q1_cond_par_q1","kir_q1_cond_par_q2","kir_q1_cond_par_q3","kir_q1_cond_par_q4","kir_q1_cond_par_q5","kir_q2_cond_par_q1","kir_q2_cond_par_q2","kir_q2_cond_par_q3","kir_q2_cond_par_q4","kir_q2_cond_par_q5","kir_q3_cond_par_q1","kir_q3_cond_par_q2","kir_q3_cond_par_q3","kir_q3_cond_par_q4","kir_q3_cond_par_q5","kir_q4_cond_par_q1","kir_q4_cond_par_q2","kir_q4_cond_par_q3","kir_q4_cond_par_q4","kir_q4_cond_par_q5","kir_q5_cond_par_q1","kir_q5_cond_par_q2","kir_q5_cond_par_q3","kir_q5_cond_par_q4","kir_q5_cond_par_q5","kfr_q1_cond_par_q1","kfr_q1_cond_par_q2","kfr_q1_cond_par_q3","kfr_q1_cond_par_q4","kfr_q1_cond_par_q5","kfr_q2_cond_par_q1","kfr_q2_cond_par_q2","kfr_q2_cond_par_q3","kfr_q2_cond_par_q4","kfr_q2_cond_par_q5","kfr_q3_cond_par_q1","kfr_q3_cond_par_q2","kfr_q3_cond_par_q3","kfr_q3_cond_par_q4","kfr_q3_cond_par_q5","kfr_q4_cond_par_q1","kfr_q4_cond_par_q2","kfr_q4_cond_par_q3","kfr_q4_cond_par_q4","kfr_q4_cond_par_q5","kfr_q5_cond_par_q1","kfr_q5_cond_par_q2","kfr_q5_cond_par_q3","kfr_q5_cond_par_q4","kfr_q5_cond_par_q5"]',
            "RENAME_MAPPINGS": '{"kid_race": "kid_race","gender": "gender","count": "count","kir_q1": "kir_q1","kir_q2": "kir_q2","kir_q3": "kir_q3","kir_q4": "kir_q4","kir_q5": "kir_q5","kfr_q1": "kfr_q1","kfr_q2": "kfr_q2","kfr_q3": "kfr_q3","kfr_q4": "kfr_q4","kfr_q5": "kfr_q5","par_q1": "par_q1","par_q2": "par_q2","par_q3": "par_q3","par_q4": "par_q4","par_q5": "par_q5","kir_q1_cond_par_q1": "kir_q1_cond_par_q1","kir_q1_cond_par_q2": "kir_q1_cond_par_q2","kir_q1_cond_par_q3": "kir_q1_cond_par_q3","kir_q1_cond_par_q4": "kir_q1_cond_par_q4","kir_q1_cond_par_q5": "kir_q1_cond_par_q5","kir_q2_cond_par_q1": "kir_q2_cond_par_q1","kir_q2_cond_par_q2": "kir_q2_cond_par_q2","kir_q2_cond_par_q3": "kir_q2_cond_par_q3","kir_q2_cond_par_q4": "kir_q2_cond_par_q4","kir_q2_cond_par_q5": "kir_q2_cond_par_q5","kir_q3_cond_par_q1": "kir_q3_cond_par_q1","kir_q3_cond_par_q2": "kir_q3_cond_par_q2","kir_q3_cond_par_q3": "kir_q3_cond_par_q3","kir_q3_cond_par_q4": "kir_q3_cond_par_q4","kir_q3_cond_par_q5": "kir_q3_cond_par_q5","kir_q4_cond_par_q1": "kir_q4_cond_par_q1","kir_q4_cond_par_q2": "kir_q4_cond_par_q2","kir_q4_cond_par_q3": "kir_q4_cond_par_q3","kir_q4_cond_par_q4": "kir_q4_cond_par_q4","kir_q4_cond_par_q5": "kir_q4_cond_par_q5","kir_q5_cond_par_q1": "kir_q5_cond_par_q1","kir_q5_cond_par_q2": "kir_q5_cond_par_q2","kir_q5_cond_par_q3": "kir_q5_cond_par_q3","kir_q5_cond_par_q4": "kir_q5_cond_par_q4","kir_q5_cond_par_q5": "kir_q5_cond_par_q5","kfr_q1_cond_par_q1": "kfr_q1_cond_par_q1","kfr_q1_cond_par_q2": "kfr_q1_cond_par_q2","kfr_q1_cond_par_q3": "kfr_q1_cond_par_q3","kfr_q1_cond_par_q4": "kfr_q1_cond_par_q4","kfr_q1_cond_par_q5": "kfr_q1_cond_par_q5","kfr_q2_cond_par_q1": "kfr_q2_cond_par_q1","kfr_q2_cond_par_q2": "kfr_q2_cond_par_q2","kfr_q2_cond_par_q3": "kfr_q2_cond_par_q3","kfr_q2_cond_par_q4": "kfr_q2_cond_par_q4","kfr_q2_cond_par_q5": "kfr_q2_cond_par_q5","kfr_q3_cond_par_q1": "kfr_q3_cond_par_q1","kfr_q3_cond_par_q2": "kfr_q3_cond_par_q2","kfr_q3_cond_par_q3": "kfr_q3_cond_par_q3","kfr_q3_cond_par_q4": "kfr_q3_cond_par_q4","kfr_q3_cond_par_q5": "kfr_q3_cond_par_q5","kfr_q4_cond_par_q1": "kfr_q4_cond_par_q1","kfr_q4_cond_par_q2": "kfr_q4_cond_par_q2","kfr_q4_cond_par_q3": "kfr_q4_cond_par_q3","kfr_q4_cond_par_q4": "kfr_q4_cond_par_q4","kfr_q4_cond_par_q5": "kfr_q4_cond_par_q5","kfr_q5_cond_par_q1": "kfr_q5_cond_par_q1","kfr_q5_cond_par_q2": "kfr_q5_cond_par_q2","kfr_q5_cond_par_q3": "kfr_q5_cond_par_q3","kfr_q5_cond_par_q4": "kfr_q5_cond_par_q4","kfr_q5_cond_par_q5": "kfr_q5_cond_par_q5"}',
            "PIPELINE_NAME": "national_child_and_parent_income_transition_matrices_by_race_and_gender",
        },
        resources={"limit_memory": "2G", "limit_cpu": "1"},
    )

    # Task to load CSV data to a BigQuery table
    load_income_transition_to_bq = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id="load_income_transition_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=[
            "data/race_and_economic_opportunity/national_child_and_parent_income_transition_matrices_by_race_and_gender/data_output.csv"
        ],
        source_format="CSV",
        destination_project_dataset_table="race_and_economic_opportunity.national_child_and_parent_income_transition_matrices_by_race_and_gender",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {"name": "kid_race", "type": "STRING", "mode": "NULLABLE"},
            {"name": "gender", "type": "STRING", "mode": "NULLABLE"},
            {"name": "count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "kir_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q1_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q1_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q1_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q1_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q1_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q2_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q3_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q4_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_q5_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q1_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q2_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q3_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q4_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5_cond_par_q1", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5_cond_par_q2", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5_cond_par_q3", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5_cond_par_q4", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_q5_cond_par_q5", "type": "FLOAT", "mode": "NULLABLE"},
        ],
    )

    income_transition_transform_csv >> load_income_transition_to_bq
