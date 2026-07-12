# api

A small FastAPI service so the model can be served instead of only writing CSVs.
This is the production face of the project.

Run it:

    uvicorn api.main:app --reload --port 8000

Then open http://localhost:8000/docs for the Swagger UI where you can click
through every endpoint.

Endpoints:

  GET  /health                        is it up, is tracing on
  GET  /territory/{id}/beat-plan       ranked visit list for a territory
  GET  /retailer/{id}/score            score plus SHAP explanation for one retailer
  POST /retailer/{id}/next-action      SALAH recommendation, body picks the language
  POST /outcome                        log a visit outcome into SEEKHO
  GET  /eval                           current evaluation report

It loads the pipeline outputs lazily on the first request, so the service starts
even if you have not run the pipeline yet (you just get a 503 telling you to run
it). Every request goes through the tracer, so if Langfuse is configured you can
watch traffic come through in the dashboard.

Note this serves whatever is in outputs/. Re run the pipeline to refresh what the
API returns. In a real deployment you would put a scheduled pipeline run behind
this and have the API reload, but for a portfolio project the lazy load is fine.
