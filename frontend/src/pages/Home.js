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
  const [showAuthPassword, setShowAuthPassword] = useState(false);
  const [showAuthConfirmPassword, setShowAuthConfirmPassword] = useState(false);
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
    <div className="min-h-screen bg-[#0b1220] text-slate-100 overflow-hidden relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.12),_transparent_55%)] pointer-events-none" />
      <div className="absolute -right-24 top-20 h-72 w-72 bg-blue-600/20 blur-3xl rounded-full pointer-events-none animate-pulse" />
      <div className="absolute left-10 bottom-20 h-40 w-40 bg-purple-500/20 blur-3xl rounded-full pointer-events-none animate-pulse" />

      <header className="relative z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center overflow-hidden">
              <img src={logo} alt="Sahakari Bot" className="w-full h-full object-contain" />
            </div>
            <span className="text-sm font-semibold tracking-wide">
              Sahakari Bot
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-xs uppercase tracking-[0.2em] text-slate-400">
            <a className="hover:text-white transition" href="#about">
              About
            </a>
            <a className="hover:text-white transition" href="#platform">
              Platform
            </a>
            <a className="hover:text-white transition" href="#assurance">
              Assurance
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
        <section id="about" className="max-w-6xl mx-auto px-4 sm:px-6 py-12 lg:py-20">
          <div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-12 items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-slate-400 mb-4">
                Compliance intelligence
              </p>
              <h1 className="text-4xl sm:text-6xl font-semibold leading-tight">
                SAHAKARI
                <span className="text-blue-400"> BOT</span>
              </h1>
              <p className="mt-5 text-slate-400 text-base sm:text-lg max-w-xl">
                Transform complex security policies into clear, actionable
                guidance. Sahakari Bot helps teams answer compliance questions
                with traceable references and instant insights.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
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
              <div className="mt-10 flex items-center gap-6 text-xs text-slate-400">
                <span className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  Verified sources
                </span>
                <span className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                  Secure by design
                </span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-8 -left-8 h-24 w-24 border border-slate-700/50 rounded-3xl rotate-12" />
              <div className="absolute -bottom-10 right-8 h-16 w-16 border border-slate-700/50 rounded-2xl -rotate-6" />
              <div className="bg-slate-950/80 border border-slate-800 rounded-[2.5rem] p-6 shadow-2xl">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-6">
                  <span className="uppercase tracking-[0.3em]">Live</span>
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="text-3xl font-semibold tracking-tight">
                    Policy Intelligence
                  </div>
                  <p className="text-sm text-slate-400">
                    Consolidate regulatory obligations, audit actions, and
                    security requirements into a single command center.
                  </p>
                  <div className="grid gap-3">
                    {[
                      "Incident response timelines",
                      "Vendor risk due diligence",
                      "Zero-trust access controls",
                    ].map((item) => (
                      <div
                        key={item}
                        className="bg-[#0b1220] border border-slate-800 rounded-2xl px-4 py-3 text-sm text-slate-200 flex items-center justify-between"
                      >
                        <span>{item}</span>
                        <span className="text-blue-400">→</span>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
                    <span>Updated recently</span>
                    <span className="flex items-center gap-2">
                      <img src={logo} alt="Sahakari Bot" className="w-4 h-4 object-contain" />
                      Sahakari AI
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 flex flex-wrap items-center justify-between gap-6 text-xs uppercase tracking-[0.3em] text-slate-500">
            <span>01 Governance</span>
            <span>02 Risk</span>
            <span>03 Compliance</span>
            <span>04 Reporting</span>
          </div>
        </section>

        <section id="platform" className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                title: "Context-rich answers",
                desc: "Every response links to source documents for audit-grade confidence.",
              },
              {
                title: "Adaptive guidance",
                desc: "Understand policy gaps and recommend next-best actions instantly.",
              },
              {
                title: "Executive-ready insights",
                desc: "Summaries tailored for leadership, compliance, and security teams.",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/40 transition"
              >
                <h3 className="text-lg font-semibold mb-3">{card.title}</h3>
                <p className="text-sm text-slate-400">{card.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="assurance" className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
          <div className="bg-gradient-to-r from-slate-950 via-[#0b1220] to-slate-900 border border-slate-800 rounded-3xl p-8 md:p-12 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Assurance ready
              </p>
              <h3 className="text-2xl font-semibold mt-3">
                Bring audit-grade intelligence to every decision.
              </h3>
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
                <div className="relative">
                  <input
                    type={showAuthPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    className="w-full px-4 py-3 pr-12 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowAuthPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-100 transition"
                    aria-label={
                      showAuthPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showAuthPassword ? (
                      <svg
                        className="w-5 h-5 transition-transform duration-200 rotate-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10a9.97 9.97 0 012.1-6.125m2.15 2.15A9.96 9.96 0 0012 5c5.523 0 10 4.477 10 10a9.97 9.97 0 01-4.2 8.125M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 3l18 18"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="w-5 h-5 transition-transform duration-200 rotate-180"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {authMode === "register" && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Confirm password
                  </label>
                  <div className="relative">
                    <input
                      type={showAuthConfirmPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(event) =>
                        setConfirmPassword(event.target.value)
                      }
                      required
                      className="w-full px-4 py-3 pr-12 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Re-enter your password"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setShowAuthConfirmPassword((prev) => !prev)
                      }
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-100 transition"
                      aria-label={
                        showAuthConfirmPassword
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {showAuthConfirmPassword ? (
                        <svg
                          className="w-5 h-5 transition-transform duration-200 rotate-0"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10a9.97 9.97 0 012.1-6.125m2.15 2.15A9.96 9.96 0 0012 5c5.523 0 10 4.477 10 10a9.97 9.97 0 01-4.2 8.125M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M3 3l18 18"
                          />
                        </svg>
                      ) : (
                        <svg
                          className="w-5 h-5 transition-transform duration-200 rotate-180"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                          />
                        </svg>
                      )}
                    </button>
                  </div>
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
