# GitHub Issue: Use .env for SQL Warehouse ID and Service Principal

**Open this issue here:** https://github.com/dediggibyte/databricks_dqx_agent/issues/new

Copy the **Title** and **Body** below into the new issue form.

---

## Title

```
[Config] Use .env for SQL Warehouse ID and Service Principal instead of hardcoding
```

---

## Body

```markdown
## Summary

`sql_warehouse_id` and `service_principal_name` are currently hardcoded in `environments/dev/variables.yml`. For security and flexibility they should be provided via environment variables (local `.env`) or CI secrets, rather than committed to the repo.

## Suggested approach

1. **Declare variables in root `databricks.yml`**  
   Ensure both are declared (e.g. with `default: ""`) so target overrides and `--var` work correctly.

2. **Add `.env.example`** (committed) with placeholders:
   - `SQL_WAREHOUSE_ID`
   - `SERVICE_PRINCIPAL_NAME`  
   Document that users copy to `.env` and set values. Keep `.env` in `.gitignore`.

3. **Stop hardcoding in `environments/dev/variables.yml`**  
   Remove the literal values for `sql_warehouse_id` and `service_principal_name`; use empty defaults so values are supplied via `--var` or env.

4. **Local deploy script**  
   Add a script (e.g. `scripts/deploy-dev.sh`) that:
   - Sources `.env` if present
   - Checks that `SQL_WAREHOUSE_ID` and `SERVICE_PRINCIPAL_NAME` are set
   - Runs `databricks bundle validate` and `databricks bundle deploy -t dev` with:
     - `--var "sql_warehouse_id=$SQL_WAREHOUSE_ID"`
     - `--var "service_principal_name=$SERVICE_PRINCIPAL_NAME"`

5. **CI/CD**  
   - In the deploy action, add an optional input (e.g. `service-principal-name`) and pass it as `--var service_principal_name=...` whenever it's non-empty (in addition to existing `sql_warehouse_id`).
   - In the workflow that calls the deploy action, pass the new value from a secret (e.g. `secrets.SERVICE_PRINCIPAL_NAME`).
   - Document that the **dev** (and any other relevant) GitHub environment needs a `SERVICE_PRINCIPAL_NAME` secret.

## Benefits

- No secrets in version control
- Each developer/environment can use different warehouse and service principal without changing code
- CI continues to use GitHub secrets; local dev uses `.env`

## Reference

This was implemented in a fork; the maintainer can adopt the same pattern or adapt it to repo conventions.
```
