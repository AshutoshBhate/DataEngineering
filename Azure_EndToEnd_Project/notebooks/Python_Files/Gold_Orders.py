# Databricks notebook source
# MAGIC %md
# MAGIC # **Fact Orders**

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Data Reading**

# COMMAND ----------

df = spark.sql("select * from databricks_cata.silver.orders_silver")
df.display()

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from databricks_cata.gold.dimproducts

# COMMAND ----------

df_dimcus = spark.sql("select DimCustomerKey, customer_id as dim_customer from databricks_cata.gold.dimcustomers")

df_dimpro = spark.sql("select product_id as DimProductKey, product_id as dim_product from databricks_cata.gold.dimproducts")

# COMMAND ----------

# MAGIC %md
# MAGIC **Fact DataFrame**

# COMMAND ----------

df_fact = df.join(df_dimcus, df.customer_id == df_dimcus.dim_customer, 'left').join(df_dimpro, df['product_id'] == df_dimpro['dim_product'], 'left')

df_fact_new = df_fact.drop('dim_customer', 'dim_product', 'customer_id', 'product_id')


# COMMAND ----------

df_fact_new.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Upsert on Fact Table**

# COMMAND ----------

from delta.tables import DeltaTable
from pyspark.sql.functions import col


# COMMAND ----------

if spark.catalog.tableExists("databricks_cata.gold.FactOrders"):
    # If the table exists, get a reference to it
    fact_table = DeltaTable.forName(spark, "databricks_cata.gold.FactOrders")

    # Perform the upsert (merge) operation
    fact_table.alias("trg").merge(
        df_fact_new.alias("src"),
        "trg.order_id = src.order_id AND trg.DimCustomerKey = src.DimCustomerKey AND trg.DimProductKey = src.DimProductKey"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

else:
    # If the table does not exist, create it for the first time
    df_fact_new.write.format("delta").option("path", "abfss://gold@databrickscygnusete.dfs.core.windows.net/FactOrders").saveAsTable("databricks_cata.gold.FactOrders")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from databricks_cata.gold.FactOrders

# COMMAND ----------

