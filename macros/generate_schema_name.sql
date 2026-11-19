{#
  By default dbt prefixes custom schemas with the target schema
  (public_bronze, public_silver...). This keeps the plain names
  bronze / silver / gold, which match the layer names in the docs.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
