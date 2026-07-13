app.post("/survey", (req, res) => {
  if (process.env.NODE_ENV !== "production") {
    console.log("Survey response:", req.body);
  }

  // 저장 처리
  saveSurvey(req.body);

  res.json({ success: true });
});