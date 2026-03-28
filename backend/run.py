import uvicorn

if __name__ == "__main__":
    # 启动 FastAPI 应用
    # reload=True 表示开启热更新，在开发阶段代码修改后会自动重启服务
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)