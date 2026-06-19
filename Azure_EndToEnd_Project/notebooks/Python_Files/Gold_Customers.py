# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# COMMAND ----------

init_load_flag = int(dbutils.widgets.get("init_load_flag"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Data Reading from source**

# COMMAND ----------

df = spark.sql("select * from databricks_cata.silver.customers_silver")

# COMMAND ----------

df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Remove Duplicates**

# COMMAND ----------

df = df.dropDuplicates(subset = ['customer_id'])
df.limit(10).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Assign a surrogate key column to our DataFrame**

# COMMAND ----------

# MAGIC %md
# MAGIC ### Surrogate key is a pseudokey that we create in our dimension so that we can easily apply joins
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## **Dividing New vs Old Records**

# COMMAND ----------

if init_load_flag == 0:
    df_old = spark.sql("""
        select DimCustomerKey, customer_id, create_date, update_date 
        from databricks_cata.gold.DimCustomers
    """)

else:
    df_old = spark.sql("""
        select 0 DimCustomerKey, 0 customer_id, 0 create_date, 0 update_date
        from databricks_cata.silver.customers_silver 
        where 1 = 0
    """)

# COMMAND ----------

df_old.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Renaming columns of df_old**

# COMMAND ----------

df_old = df_old.withColumnRenamed("DimCustomerKey", "old_DimCustomerKey").withColumnRenamed("customer_id", "old_customer_id").withColumnRenamed("create_date", "old_create_date").withColumnRenamed("update_date", "old_update_date")

# COMMAND ----------

df_old.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Applying join with the old records**

# COMMAND ----------

df_join = df.join(df_old, df.customer_id == df_old.old_customer_id, 'left')

# COMMAND ----------

#All the values will be null as this is an initial load

df_join.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Separating New vs Old Records**

# COMMAND ----------

df_new = df_join.filter(df_old.old_DimCustomerKey.isNull())

# COMMAND ----------

#Already added in gold

df_old = df_join.filter(df_old.old_DimCustomerKey.isNotNull())

# COMMAND ----------

# MAGIC %md
# MAGIC **Preparing df_old**

# COMMAND ----------

#Dropping all the columns which are not required
df_old = df_old.drop("old_customer_id", "old_update_date")

#Renaming "old_DimCustomerKey" to "DimCustomerKey"
df_old = df_old.withColumnRenamed("old_DimCustomerKey", "DimCustomerKey")

#Renaming old_create_date column to create_date
df_old = df_old.withColumnRenamed("old_create_date", "create_date")
df_old = df_old.withColumn("create_date", to_timestamp(col("create_date")))

#Recreating update_date column
df_old = df_old.withColumn("update_date", current_timestamp())

# COMMAND ----------

df_old.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Preparing df_new**

# COMMAND ----------

df_new.display()

# COMMAND ----------

#Dropping all the columns which are not required
df_new = df_new.drop("old_DimCustomerKey", "old_customer_id", "old_update_date", "old_create_date")

#Recreating "update_date", "create_date" columns with current timestamp
df_new = df_new.withColumn("create_date", current_timestamp())
df_new = df_new.withColumn("update_date", current_timestamp())

# COMMAND ----------

df_new.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Surrogate Key - From 1**

# COMMAND ----------

windowSpec = Window.orderBy(col("customer_id"))

# COMMAND ----------

# MAGIC %md
# MAGIC **Adding Max Surrogate Key**

# COMMAND ----------

if init_load_flag == 1:
    max_surrogate_key = 0
else:
    df_maxsur = spark.sql("select max(DimCustomerKey) as max_surrogate_key from databricks_cata.gold.DimCustomers")
    max_surrogate_key = df_maxsur.collect()[0]['max_surrogate_key']
    if max_surrogate_key is None:
        max_surrogate_key = 0

df_new = df_new.withColumn("DimCustomerKey", lit(max_surrogate_key) + row_number().over(windowSpec))

df_new.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Union of df_old and df_new**

# COMMAND ----------

df_final = df_new.unionByName(df_old)

# COMMAND ----------

df_final.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ##**SCD Type-1**

# COMMAND ----------

#Not the part of actual code

if spark.catalog.tableExists("databricks_cata.gold.DimCustomers"):
    print("Hello")
else:
    print("Broo")

# COMMAND ----------

from delta.tables import DeltaTable

# COMMAND ----------

if spark.catalog.tableExists("databricks_cata.gold.DimCustomers"):
    #dlt_obj is the target, our main table where we have to apply our merge condition
    dlt_obj = DeltaTable.forPath(spark, "abfss://gold@databrickscygnusete.dfs.core.windows.net/DimCustomers")

    dlt_obj.alias("trg").merge(df_final.alias("src"), "trg.DimCustomerKey = src.DimCustomerKey").whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

else:
    df_final.write.mode("overwrite").format("delta").option("path", "abfss://gold@databrickscygnusete.dfs.core.windows.net/DimCustomers").saveAsTable("databricks_cata.gold.DimCustomers")
 

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM databricks_cata.gold.dimcustomers

# COMMAND ----------

