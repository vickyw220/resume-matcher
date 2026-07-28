import { useState } from "react";
import "./App.css";

function App() {
  const [jdText, setJdText] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!resumeFile || !jdText.trim()) {
      setError("Please upload a resume and paste a job description.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("jd_text", jdText);
      formData.append("resume_file", resumeFile);

      const response = await fetch("https://resume-matcher-production-b5eb.up.railway.app/match-pdf", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Something went wrong. Please try again.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Resume Matcher</h1>
      <p className="subtitle">
        Upload your resume and a job description to see how well you match.
      </p>

      <form onSubmit={handleSubmit} className="form">
        <label>
          Resume (PDF)
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setResumeFile(e.target.files[0])}
          />
        </label>

        <label>
          Job Description
          <textarea
            rows={10}
            placeholder="Paste the job description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Check My Match"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          <h2>Match Score: {Math.round(result.match_score * 100)}%</h2>

          <div className="skills-section">
            <h3>✅ Matched Skills</h3>
            <ul>
              {result.matched_skills.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          </div>

          <div className="skills-section">
            <h3>❌ Missing Skills</h3>
            <ul>
              {result.missing_skills.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          </div>

          <div className="suggestions-section">
            <h3>💡 Suggestions</h3>
            <ul>
              {result.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;