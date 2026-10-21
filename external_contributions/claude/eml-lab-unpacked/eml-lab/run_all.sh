#!/usr/bin/env bash
# Reproduce everything. Total ~10 min on a laptop (03c is the slow one, ~3 min). Outputs go to results/.
set -e
cd "$(dirname "$0")"
pip install -r requirements.txt
mkdir -p results
python -m unittest discover -s tests                      > results/00_tests.txt          # < 1 s
python scripts/01_counts.py                               > results/01_counts.txt
python scripts/02_export_expressions.py                   > results/02_export.txt
python scripts/03_verify_mp.py                            > results/03_verify_mp.txt      # Sub/Add/M/V (V grid |x*y|<=4)
python scripts/03c_verify_V_y3.py                         > results/03c_verify_V_y3.txt   # V with y=3 (needs up to ~7600 digits, ~3 min)
python scripts/04_float64_bench.py                        > results/04_float64_bench.txt
python scripts/05_execution_metrics.py                    > results/05_execution_metrics.txt
python scripts/06_search.py --points wide   --nmax 12     > results/06_search_wide.txt
python scripts/06_search.py --points narrow --nmax 10 --targets x-y,x+y,-x > results/06_search_narrow.txt
python scripts/07_validate_external_claims.py             > results/07_validate_external_claims.txt
# independent cross-check (shares no code with eml_lab):
python tools/independent_check.py expressions/M_opt.rpn mul --dps 450 --points "3,3;-2,0.5;0,1;1,1" > results/08_independent_M.txt
python tools/independent_check.py expressions/V_opt.rpn div --dps 300 --points "1.5,2;-2,0.5;1,-1"   > results/08_independent_V.txt
echo ALL DONE
