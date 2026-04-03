streamlit run app/channels/web_streamlit.py - Run to open streamlit in localhost
uvicorn app.api.main:app --reload - Run to open sever
python -m scripts.run_evaluation - Run to evaluation project

git add . ; git commit -m "Update streamlit_app.py to create new UI versionr" ; git push origin main -- Run to update local to github