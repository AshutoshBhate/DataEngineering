# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Data Reading**

# COMMAND ----------

df = spark.read.format("parquet").load("abfss://bronze@databrickscygnusete.dfs.core.windows.net/products")

# COMMAND ----------

df.display()

# COMMAND ----------

df.createOrReplaceTempView("products")

# COMMAND ----------

df = df.drop("_rescued_data")
df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Functions**

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION databricks_cata.bronze.discount_func(p_price DOUBLE)
# MAGIC RETURNS DOUBLE 
# MAGIC LANGUAGE SQL
# MAGIC RETURN p_price * 0.90

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT product_id, price, databricks_cata.bronze.discount_func(price) as discounted_price FROM products

# COMMAND ----------

#Apply the function to DataFrame directly, instead of views : SQL way using expr()

df = df.withColumn("discounted_price", expr("databricks_cata.bronze.discount_func(price)"))
df.display()

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION databricks_cata.bronze.upper_func(p_brand STRING)
# MAGIC RETURNS STRING
# MAGIC LANGUAGE PYTHON
# MAGIC AS
# MAGIC $$
# MAGIC   return p_brand.upper()
# MAGIC $$

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT product_id, brand, databricks_cata.bronze.upper_func(brand) as brand_upper FROM products

# COMMAND ----------

df.write.mode("overwrite").format("delta").save("abfss://silver@databrickscygnusete.dfs.core.windows.net/products").save()

# COMMAND ----------

# MAGIC %sql CREATE TABLE IF NOT EXISTS databricks_cata.silver.products_silver
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://silver@databrickscygnusete.dfs.core.windows.net/products'

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM databricks_cata.silver.products_silver

# COMMAND ----------

