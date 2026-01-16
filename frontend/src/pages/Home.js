import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logo from "../assets/logo.png";

const Home = ({ initialAuthMode = null }) => {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const [authOpen, setAuthOpen] = useState(Boolean(initialAuthMode));
  const [authMode, setAuthMode] = useState(initialAuthMode || "login");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialAuthMode) {
      setAuthMode(initialAuthMode);
      setAuthOpen(true);
    }
  }, [initialAuthMode]);

  const openAuth = (mode) => {
    setAuthMode(mode);
    setAuthOpen(true);
    setError("");
  };

  const closeAuth = () => {
    setAuthOpen(false);
    setError("");
    if (initialAuthMode) {
      navigate("/");
    }
  };

  useEffect(() => {
    if (!authOpen) return;
    const handleEscape = (event) => {
      if (event.key === "Escape") {
        closeAuth();
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [authOpen, closeAuth]);

  const handleAuthSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    if (authMode === "register") {
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        setLoading(false);
        return;
      }

      if (password.length < 6) {
        setError("Password must be at least 6 characters");
        setLoading(false);
        return;
      }
    }

    const result =
      authMode === "login"
        ? await login(email, password)
        : await register(email, username, password);

    if (result.success) {
      setAuthOpen(false);
      navigate("/chat");
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#0b1220] text-slate-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.15),_transparent_55%)] pointer-events-none" />
      <header className="relative z-10 border-b border-slate-800 bg-slate-950/60 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center overflow-hidden">
              <img src={logo} alt="Sahakari Bot" className="w-full h-full object-contain" />
            </div>
            <div>
              <p className="text-sm font-semibold">Sahakari Bot</p>
              <p className="text-xs text-slate-400">Compliance intelligence</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-400">
            <a className="hover:text-slate-100 transition" href="#features">
              Features
            </a>
            <a className="hover:text-slate-100 transition" href="#workflow">
              Workflow
            </a>
            <a className="hover:text-slate-100 transition" href="#security">
              Security
            </a>
          </nav>
          <div className="flex items-center gap-2">
            {user ? (
              <Link
                to="/chat"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
              >
                Open chat
              </Link>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => openAuth("login")}
                  className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white border border-slate-800 rounded-xl bg-slate-900/60 transition"
                >
                  Sign in
                </button>
                <button
                  type="button"
                  onClick={() => openAuth("register")}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
                >
                  Get started
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="relative z-10">
        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 lg:py-24">
          <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-10 items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-4">
                Compliance copilots for high-trust teams
              </p>
              <h1 className="text-3xl sm:text-5xl font-semibold leading-tight">
                Navigate cybersecurity standards with confidence using your own
                documents.
              </h1>
              <p className="mt-5 text-slate-400 text-base sm:text-lg max-w-xl">
                Sahakari Bot turns internal policies, audit reports, and
                regulatory documents into a secure, searchable assistant—built
                for risk managers, compliance officers, and security leaders.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                {user ? (
                  <Link
                    to="/chat"
                    className="px-5 py-3 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
                  >
                    Continue in chat
                  </Link>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => openAuth("register")}
                      className="px-5 py-3 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
                    >
                      Start free
                    </button>
                    <button
                      type="button"
                      onClick={() => openAuth("login")}
                      className="px-5 py-3 text-sm font-medium text-slate-200 border border-slate-800 rounded-xl bg-slate-900/60 hover:text-white transition"
                    >
                      Sign in
                    </button>
                  </>
                )}
              </div>
              <div className="mt-8 grid grid-cols-3 gap-4 max-w-md">
                {[
                  { label: "Policies indexed", value: "1.2k+" },
                  { label: "Avg. response", value: "4.6s" },
                  { label: "Audit ready", value: "99%" },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4"
                  >
                    <p className="text-lg font-semibold">{stat.value}</p>
                    <p className="text-xs text-slate-400">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-3xl p-6 shadow-xl">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-4">
                <span>Live workspace</span>
                <span className="bg-slate-800 text-slate-200 px-2 py-1 rounded-full">
                  Secure mode
                </span>
              </div>
              <div className="space-y-4">
                <div className="bg-[#0b1220] border border-slate-800 rounded-2xl p-4 text-sm text-slate-200">
                  Which policies define incident response reporting timelines?
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-sm text-slate-100">
                  The Incident Response Standard v4.2 requires notification
                  within 72 hours for P1 incidents. See section 3.1 and Appendix
                  B for SLA exceptions.
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-400">
                  Sources: IR-Standard.pdf • Page 12 • Relevance 93%
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          id="features"
          className="max-w-6xl mx-auto px-4 sm:px-6 py-12 lg:py-16"
        >
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-10">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Purpose built
              </p>
              <h2 className="text-2xl sm:text-3xl font-semibold mt-2">
                A professional compliance workspace.
              </h2>
            </div>
            <p className="text-sm text-slate-400 max-w-md">
              Keep your team aligned with a single source of truth and audit
              ready citations, aligned to regulatory requirements.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: "Citation-ready answers",
                desc: "Every response includes document citations for audit trails and executive reporting.",
              },
              {
                title: "Policy-aware memory",
                desc: "Contextual understanding tied to your policies, standards, and risk registers.",
              },
              {
                title: "Operational speed",
                desc: "Accelerate assessments, vendor reviews, and policy updates in seconds.",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6"
              >
                <h3 className="text-lg font-semibold mb-3">{card.title}</h3>
                <p className="text-sm text-slate-400">{card.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section
          id="workflow"
          className="max-w-6xl mx-auto px-4 sm:px-6 py-12 lg:py-16"
        >
          <div className="grid lg:grid-cols-2 gap-8">
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-3">Focused workflows</h3>
              <p className="text-sm text-slate-400 mb-6">
                Organize compliance activities across regulations, audits, and
                internal policy updates without switching tools.
              </p>
              <ul className="space-y-3 text-sm text-slate-300">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Prepare audit responses with linked evidence.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Track coverage of regulatory obligations.
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  Summarize risk controls for leadership updates.
                </li>
              </ul>
            </div>
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-3">Insights dashboard</h3>
              <p className="text-sm text-slate-400 mb-6">
                Quickly validate compliance posture with smart summaries, gap
                highlights, and recommended follow-ups.
              </p>
              <div className="grid gap-4">
                {[
                  "Policy coverage gap: Vendor due diligence",
                  "Upcoming audit: ISO 27001 readiness",
                  "Open items: 4 controls pending review",
                ].map((item) => (
                  <div
                    key={item}
                    className="bg-[#0b1220] border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section
          id="security"
          className="max-w-6xl mx-auto px-4 sm:px-6 py-12 lg:py-16"
        >
          <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 md:p-10">
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Security first
                </p>
                <h3 className="text-2xl font-semibold mt-3">
                  Built for regulated environments.
                </h3>
              </div>
              <div className="md:col-span-2 grid sm:grid-cols-2 gap-6 text-sm text-slate-300">
                {[
                  "Private document processing with role-based access.",
                  "Audit-grade logging for every response.",
                  "Data retention aligned with internal policies.",
                  "Configurable AI guardrails for policy consistency.",
                ].map((item) => (
                  <div
                    key={item}
                    className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 lg:py-20">
          <div className="bg-gradient-to-r from-blue-600/20 via-slate-900 to-slate-950 border border-blue-500/30 rounded-3xl p-8 md:p-12 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h3 className="text-2xl font-semibold">
                Ready to build your compliance workspace?
              </h3>
              <p className="text-sm text-slate-300 mt-3 max-w-xl">
                Invite your team, connect your policies, and start asking
                confident questions with traceable answers.
              </p>
            </div>
            <div className="flex items-center gap-3">
              {user ? (
                <Link
                  to="/chat"
                  className="px-5 py-3 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
                >
                  Open chat
                </Link>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => openAuth("register")}
                    className="px-5 py-3 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition"
                  >
                    Create account
                  </button>
                  <button
                    type="button"
                    onClick={() => openAuth("login")}
                    className="px-5 py-3 text-sm font-medium text-slate-200 border border-slate-800 rounded-xl bg-slate-900/60 hover:text-white transition"
                  >
                    Sign in
                  </button>
                </>
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 py-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between text-xs text-slate-500">
          <span>© 2026 Sahakari Bot. All rights reserved.</span>
          <div className="flex gap-4">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Security</span>
          </div>
        </div>
      </footer>

      {authOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center px-4 py-8">
          <button
            type="button"
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={closeAuth}
            aria-label="Close authentication modal"
          />
          <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl p-6">
            <div className="flex items-start justify-between gap-4 mb-6">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Secure access
                </p>
                <h2 className="text-xl font-semibold mt-2">
                  {authMode === "login" ? "Welcome back" : "Create your account"}
                </h2>
              </div>
              <button
                type="button"
                onClick={closeAuth}
                className="text-slate-400 hover:text-slate-100 transition"
                aria-label="Close modal"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 bg-slate-950/60 border border-slate-800 rounded-2xl p-1 text-sm mb-6">
              <button
                type="button"
                onClick={() => {
                  setAuthMode("login");
                  setError("");
                }}
                className={`py-2 rounded-xl transition ${
                  authMode === "login"
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                Sign in
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthMode("register");
                  setError("");
                }}
                className={`py-2 rounded-xl transition ${
                  authMode === "register"
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                Create account
              </button>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-900/40 border border-red-700 text-red-200 text-sm rounded-xl px-4 py-3">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="you@company.com"
                />
              </div>

              {authMode === "register" && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    required
                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Choose a username"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your password"
                />
              </div>

              {authMode === "register" && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Confirm password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    required
                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Re-enter your password"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading
                  ? authMode === "login"
                    ? "Signing in..."
                    : "Creating account..."
                  : authMode === "login"
                  ? "Sign in"
                  : "Create account"}
              </button>
            </form>

            <div className="mt-5 text-xs text-slate-400 text-center">
              {authMode === "login" ? (
                <>
                  New to Sahakari Bot?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("register");
                      setError("");
                    }}
                    className="text-blue-400 hover:text-blue-300"
                  >
                    Create an account
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("login");
                      setError("");
                    }}
                    className="text-blue-400 hover:text-blue-300"
                  >
                    Sign in
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
