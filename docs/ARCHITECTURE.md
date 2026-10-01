# ARCHITECTURE

> STUB. Filled in once the stack and cluster approach are decided. Write concrete facts only.

## Cluster (minimum 1 master + 2 workers)
| Node (hostname) | Role | Services | IP / port notes |
|---|---|---|---|
| OPEN | master | OPEN | OPEN |
| OPEN | worker 1 | OPEN | OPEN |
| OPEN | worker 2 | OPEN | OPEN |

- Cluster approach (Docker / VMs / cloud): OPEN
- Versions: OPEN
- Config locations: `config/`

## Pipeline
ingestion -> processing -> analytics -> output (details OPEN)

## File map
| Folder | What it does |
|---|---|
| `dataset/` | source data or pointers to it |
| `src/ingestion/` | loading data into distributed storage |
| `src/processing/` | distributed processing jobs |
| `src/analytics/` | analysis on processed data |
| `scripts/` | cluster setup/start/stop and run scripts |
| `config/` | cluster and job configs |
| `output/` | results |
| `screenshots/` | demo evidence |
| `pipeline/` | end-to-end orchestration |
