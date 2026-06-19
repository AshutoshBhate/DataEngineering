# Databricks notebook source
df = spark.read.table("databricks_cata.bronze.regions")
df.display()

# COMMAND ----------

df = df.drop("_rescued_data")

# COMMAND ----------

df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save("abfss://silver@databrickscygnusete.dfs.core.windows.net/regions")

# COMMAND ----------

df = spark.read.format("delta").load("abfss://silver@databrickscygnusete.dfs.core.windows.net/regions")

# COMMAND ----------

df.display()

# COMMAND ----------

df = spark.read.format("delta").load("abfss://silver@databrickscygnusete.dfs.core.windows.net/orders")
df.display()

# COMMAND ----------

df = spark.read.format("delta").load("abfss://silver@databrickscygnusete.dfs.core.windows.net/customers")
df.display()

# COMMAND ----------

df = spark.read.format("delta").load("abfss://silver@databrickscygnusete.dfs.core.windows.net/products")
df.display()

# COMMAND ----------

# MAGIC %sql CREATE TABLE IF NOT EXISTS databricks_cata.silver.regions_silver
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://silver@databrickscygnusete.dfs.core.windows.net/regions'

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM databricks_cata.silver.regions_silver

# COMMAND ----------

