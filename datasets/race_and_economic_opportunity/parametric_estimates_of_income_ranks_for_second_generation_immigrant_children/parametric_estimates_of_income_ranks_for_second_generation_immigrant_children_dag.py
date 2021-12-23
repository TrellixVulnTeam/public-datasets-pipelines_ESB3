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
    dag_id="race_and_economic_opportunity.parametric_estimates_of_income_ranks_for_second_generation_immigrant_children",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@daily",
    catchup=False,
    default_view="graph",
) as dag:

    # Run CSV transform within kubernetes pod
    parametric_transform_csv = kubernetes_pod_operator.KubernetesPodOperator(
        task_id="parametric_transform_csv",
        startup_timeout_seconds=600,
        name="race_and_economic_opportunity_parametric_estimates_of_income_ranks_for_second_generation_immigrant_children",
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
            "SOURCE_URL": "https://www2.census.gov/ces/opportunity/race_table6a_parametric.csv",
            "SOURCE_FILE": "files/data.csv",
            "TARGET_FILE": "files/data_output.csv",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/race_and_economic_opportunity/parametric_estimates_of_income_ranks_for_second_generation_immigrant_children/data_output.csv",
            "CSV_HEADERS": '["country","n_kfr_p","kfr_p_p25","kfr_p_p25_se","kfr_p_p75","kfr_p_p75_se","n_kir_f","kir_f_p25","kir_f_p25_se","kir_f_p75","kir_f_p75_se","n_kir_m","kir_m_p25","kir_m_p25_se","kir_m_p75","kir_m_p75_se","age_in2015_mom_p","age_in2015_dad_p","age_in2015_mom_f","age_in2015_dad_f","age_in2015_mom_m","age_in2015_dad_m","us_yrs_before_mom_p","us_yrs_before_dad_p","us_yrs_before_mom_f","us_yrs_before_dad_f","us_yrs_before_mom_m","us_yrs_before_dad_m"]',
            "RENAME_MAPPINGS": '{"country": "country","n_kfr_P": "n_kfr_p","kfr_P_p25": "kfr_p_p25","kfr_P_p25_se": "kfr_p_p25_se","kfr_P_p75": "kfr_p_p75","kfr_P_p75_se": "kfr_p_p75_se","n_kir_F": "n_kir_f","kir_F_p25": "kir_f_p25","kir_F_p25_se": "kir_f_p25_se","kir_F_p75": "kir_f_p75","kir_F_p75_se": "kir_f_p75_se","n_kir_M": "n_kir_m","kir_M_p25": "kir_m_p25","kir_M_p25_se": "kir_m_p25_se","kir_M_p75": "kir_m_p75","kir_M_p75_se": "kir_m_p75_se","age_in2015_mom_P": "age_in2015_mom_p","age_in2015_dad_P": "age_in2015_dad_p","age_in2015_mom_F": "age_in2015_mom_f","age_in2015_dad_F": "age_in2015_dad_f","age_in2015_mom_M": "age_in2015_mom_m","age_in2015_dad_M": "age_in2015_dad_m","us_yrs_before_mom_P": "us_yrs_before_mom_p","us_yrs_before_dad_P": "us_yrs_before_dad_p","us_yrs_before_mom_F": "us_yrs_before_mom_f","us_yrs_before_dad_F": "us_yrs_before_dad_f","us_yrs_before_mom_M": "us_yrs_before_mom_m","us_yrs_before_dad_M": "us_yrs_before_dad_m"}',
            "PIPELINE_NAME": "parametric_estimates_of_income_ranks_for_second_generation_immigrant_children",
        },
        resources={"limit_memory": "2G", "limit_cpu": "1"},
    )

    # Task to load CSV data to a BigQuery table
    load_parametric_to_bq = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id="load_parametric_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=[
            "data/race_and_economic_opportunity/parametric_estimates_of_income_ranks_for_second_generation_immigrant_children/data_output.csv"
        ],
        source_format="CSV",
        destination_project_dataset_table="race_and_economic_opportunity.parametric_estimates_of_income_ranks_for_second_generation_immigrant_children",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {"name": "country", "type": "STRING", "mode": "NULLABLE"},
            {"name": "n_kfr_p", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "kfr_p_p25", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_p_p25_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_p_p75", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kfr_p_p75_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "n_kir_f", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "kir_f_p25", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_f_p25_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_f_p75", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_f_p75_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "n_kir_m", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "kir_m_p25", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_m_p25_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_m_p75", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "kir_m_p75_se", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_mom_p", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_dad_p", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_mom_f", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_dad_f", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_mom_m", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "age_in2015_dad_m", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_mom_p", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_dad_p", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_mom_f", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_dad_f", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_mom_m", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "us_yrs_before_dad_m", "type": "FLOAT", "mode": "NULLABLE"},
        ],
    )

    parametric_transform_csv >> load_parametric_to_bq
