for PROJECT in $(gcloud projects list --format='value(projectId)')
do
  for BUCKET in $(gsutil ls -l -b -p $PROJECT gs://)
  do
    gsutil -m ls -r -l  $BUCKET** | head -n-1 | tr -s ' ' ','| xargs -i echo "$PROJECT,$BUCKET{}"  >> object_detail.csv
  done
done