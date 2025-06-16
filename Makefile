server: 
	uvicorn main:app --reload

unrelease:
	netstat -ano | findstr :8000

kill:
	taskkill /PID $(pid) /F

.PHONY: server