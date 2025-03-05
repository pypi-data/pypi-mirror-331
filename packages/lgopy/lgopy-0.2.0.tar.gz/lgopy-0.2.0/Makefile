.PHONY: deploy
deploy:
	gcloud builds submit . --config=cloudbuild.yaml --substitutions _SA_KEY_BASE64=`base64 -i keys/sa-gprstudio.json`

