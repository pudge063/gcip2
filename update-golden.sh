for pipeline in checkstyle multipipeline tasks; do
    dothat run build-pipeline -f tests/integration/data/${pipeline}/ci.py -o tests/integration/golden/${pipeline}/pipeline.gitlab-ci.yml
done
