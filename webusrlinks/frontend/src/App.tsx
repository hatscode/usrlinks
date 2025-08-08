import React, { useState, useRef, useEffect } from "react";
import {
  Container, Box, Typography, TextField, Button, Switch, FormControlLabel,
  Paper, CircularProgress, Snackbar, Alert, AppBar, Toolbar, IconButton, Tooltip,
  Menu, MenuItem, Select, InputLabel, FormControl, Chip, LinearProgress, Drawer, List, ListItem, ListItemText, Divider, Avatar, InputAdornment
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import CloseIcon from "@mui/icons-material/Close";
import GitHubIcon from "@mui/icons-material/GitHub";
import TwitterIcon from "@mui/icons-material/Twitter";
import SendIcon from "@mui/icons-material/Send";
import RadarIcon from "@mui/icons-material/Radar"; 
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import axios from "axios";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { saveAs } from "file-saver";
import XIcon from "@mui/icons-material/Close"; 
import { motion, Variants } from "framer-motion";
import TextareaAutosize from "@mui/material/TextareaAutosize";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";

// background 
const AnimatedBackground = () => (
  <Box
    sx={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      zIndex: -100,
      pointerEvents: "none",
      background: "radial-gradient(circle at 10% 20%, #0a1833 0%, #0e2233 60%, #050a18 100%)",
      animation: "bgmove 10s infinite alternate"
    }}
  >
    <style>
      {`
        @keyframes bgmove {
          0% { background-position: 0% 0%; }
          100% { background-position: 100% 100%; }
        }
      `}
    </style>
  </Box>
);

// API endpoint fallback logic
const API_BASE =
  typeof window !== "undefined" &&
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://localhost:8080"
    : "https://usrlinks.onrender.com";

const TG_BOT_API = process.env.REACT_APP_TG_BOT_API || "https://usrlinks.onrender.com";

const defaultThreads = 10;

const outputOptions = [
  { value: "", label: "None" },
  { value: "csv", label: "CSV" },
  { value: "json", label: "JSON" }
];

// list of defaul platforms
const defaultPlatforms = [
  { name: "GitHub", url: "https://github.com/%s" },
  { name: "Twitter", url: "https://twitter.com/%s" },
  { name: "Instagram", url: "https://instagram.com/%s" },
  { name: "Reddit", url: "https://reddit.com/user/%s" },
  { name: "LinkedIn", url: "https://linkedin.com/in/%s" },
  { name: "TikTok", url: "https://tiktok.com/@%s" },
  { name: "YouTube", url: "https://youtube.com/%s" },
  { name: "Twitch", url: "https://twitch.tv/%s" },
  { name: "Facebook", url: "https://facebook.com/%s" },
  { name: "Pinterest", url: "https://pinterest.com/%s" },
  { name: "Steam", url: "https://steamcommunity.com/id/%s" },
  { name: "Vimeo", url: "https://vimeo.com/%s" },
  { name: "SoundCloud", url: "https://soundcloud.com/%s" },
  { name: "Medium", url: "https://medium.com/@%s" },
  { name: "DeviantArt", url: "https://%s.deviantart.com" },
  { name: "GitLab", url: "https://gitlab.com/%s" },
  { name: "Bitbucket", url: "https://bitbucket.org/%s" },
  { name: "Keybase", url: "https://keybase.io/%s" },
  { name: "HackerNews", url: "https://news.ycombinator.com/user?id=%s" },
  { name: "CodePen", url: "https://codepen.io/%s" },
  { name: "Telegram", url: "https://t.me/%s" },
  { name: "Tumblr", url: "https://%s.tumblr.com" },
  { name: "Spotify", url: "https://open.spotify.com/user/%s" },
  { name: "Last.fm", url: "https://last.fm/user/%s" },
  { name: "Roblox", url: "https://www.roblox.com/user.aspx?username=%s" },
  { name: "Quora", url: "https://www.quora.com/profile/%s" },
  { name: "VK", url: "https://vk.com/%s" },
  { name: "Imgur", url: "https://imgur.com/user/%s" },
  { name: "Etsy", url: "https://www.etsy.com/shop/%s" },
  { name: "Pastebin", url: "https://pastebin.com/u/%s" },
];

const LOG_LIMIT = 20;

// Animated RadarIcon with rotation
const AnimatedRadar = () => (
  <motion.span
    animate={{ rotate: [0, 360] }}
    transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
    style={{ display: "inline-block" }}
  >
    <RadarIcon sx={{ color: "#00bfff", fontSize: 40 }} />
  </motion.span>
);

const App: React.FC = () => {
  const [username, setUsername] = useState("");
  const [proxy, setProxy] = useState("");
  const [tor, setTor] = useState(false);
  const [threads, setThreads] = useState(defaultThreads);
  const [output, setOutput] = useState("");
  const [deepScan, setDeepScan] = useState(false);
  const [generateDorks, setGenerateDorks] = useState(false);
  const [platformsFile, setPlatformsFile] = useState<File | null>(null);
  const [scanResults, setScanResults] = useState<any[]>([]);
  const [dorks, setDorks] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: "success" | "error" | "info" }>({ open: false, message: "", severity: "info" });
  const [showResults, setShowResults] = useState(false);
  const [showDorks, setShowDorks] = useState(false);
  const [showPlatforms, setShowPlatforms] = useState(false);
  const [platforms, setPlatforms] = useState<any>({});
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [reportType, setReportType] = useState<"csv" | "json" | "pdf">("csv");
  const [summaryModal, setSummaryModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [logsOpen, setLogsOpen] = useState(true); // for collapsible logs bar
  const [customPlatforms, setCustomPlatforms] = useState<string[]>([]);
  const [customPlatformInput, setCustomPlatformInput] = useState("");
  const [feedback, setFeedback] = useState("");
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [askNameOpen, setAskNameOpen] = useState(false);
  const [feedbackName, setFeedbackName] = useState("");
  const [platformsList, setPlatformsList] = useState(
    defaultPlatforms.map(p => ({ ...p, enabled: true, custom: false }))
  );
  const [platformsBarOpen, setPlatformsBarOpen] = useState(false);
  const [feedbacksOpen, setFeedbacksOpen] = useState(false);
  const [feedbacks, setFeedbacks] = useState<{ name: string; message: string; time?: number }[]>([]);

  // Fetch supported platforms
  const fetchPlatforms = async () => {
    try {
      const res = await axios.get(`${API_BASE}/platforms`);
      setPlatforms(res.data);
      setShowPlatforms(true);
    } catch {
      setSnackbar({ open: true, message: "Failed to fetch platforms", severity: "error" });
    }
  };

  // Fetch feedbacks from backend
  const fetchFeedbacks = () => {
    fetch(`${TG_BOT_API}/feedbacks`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setFeedbacks(data);
      })
      .catch(() => setFeedbacks([]));
  };

  useEffect(() => {
    if (feedbacksOpen) {
      fetchFeedbacks();
    }
  }, [feedbacksOpen]);

  // add mre platforms, multipe allowed
  const handleAddCustomPlatform = () => {
    if (!customPlatformInput.trim()) return;
    // extract tthe name of the platform for proper listing
    let url = customPlatformInput.trim();
    let name = url.replace(/^https?:\/\//, "").split(/[/.]/)[0];
    if (!name) name = "Custom";
    setPlatformsList(prev => [
      ...prev,
      { name, url, enabled: true, custom: true }
    ]);
    setCustomPlatformInput("");
  };
  const handleTogglePlatform = (idx: number) => {
    setPlatformsList(prev =>
      prev.map((p, i) => i === idx ? { ...p, enabled: !p.enabled } : p)
    );
  };
  const handleRemoveCustomPlatform = (idx: number) => {
    setPlatformsList(prev => prev.filter((_, i) => i !== idx));
  };

  // Add log with timestamp
  const addLog = (msg: string) =>
    setLogs(logs => [
      ...logs,
      `[${new Date().toLocaleTimeString()}] ${msg}`
    ].slice(-LOG_LIMIT));

  // Enhanced scan logging
  const handleScan = async () => {
    if (!username) {
      setSnackbar({ open: true, message: "Username is required", severity: "error" });
      return;
    }
    setLoading(true);
    setShowResults(false);
    setShowDorks(false);
    setLogs([]);
    setProgress(0);
    addLog("Scan started for username: " + username);

    let params: any = {
      threads,
      deep_scan: deepScan,
      output,
      proxy,
      tor,
      generate_dorks: generateDorks
    };
    if (platformsFile) {
      params.platforms = platformsFile.name;
    }

    try {
      if (platformsFile) {
        addLog("Uploading custom platforms file...");
        const formData = new FormData();
        formData.append("file", platformsFile);
        await axios.post(`${API_BASE}/upload_platforms`, formData, { headers: { "Content-Type": "multipart/form-data" } });
        addLog("Custom platforms file uploaded.");
      }

      // log each platform scan 
      const enabledPlatforms = platformsList.filter(p => p.enabled);
      addLog(`Scanning ${enabledPlatforms.length} platforms...`);
      for (const p of enabledPlatforms) {
        addLog(`Scanning: ${p.name} (${p.url.replace("%s", username)})`);
      }

      addLog("Sending scan request...");
      const res = await axios.get(`${API_BASE}/check/${encodeURIComponent(username)}`, { params });
      addLog("Scan response received.");

      if (generateDorks) {
        setDorks(res.data.dorks || []);
        setShowDorks(true);
        addLog("Google dorks generated.");
      } else {
        setScanResults(res.data);
        setShowResults(true);
        // Log per-platform result
        if (Array.isArray(res.data)) {
          res.data.forEach((r: any) => {
            addLog(
              `Done: ${r.platform} - ` +
              (r.available === true
                ? "AVAILABLE"
                : r.available === false
                ? "TAKEN"
                : "ERROR")
            );
          });
        }
        addLog("Scan results processed.");
        setSummaryModal(true); // shoow summary modal
      }
      setSnackbar({ open: true, message: "Scan complete!", severity: "success" });
      addLog("Scan complete.");
    } catch (e: any) {
      setSnackbar({ open: true, message: "Scan failed: " + (e?.message || "Unknown error"), severity: "error" });
      addLog("Scan failed: " + (e?.message || "Unknown error"));
    } finally {
      setLoading(false);
      setProgress(100);
    }
  };

  // Download results
  const handleDownload = (type: "csv" | "json" | "pdf") => {
    if (!scanResults.length) return;
    if (type === "csv") {
      const header = ["Platform", "Status", "URL", "Emails", "Phones", "URLs", "Location", "Bio"];
      const rows = scanResults.map(r => [
        r.platform,
        r.available === true ? "AVAILABLE" : r.available === false ? "TAKEN" : "ERROR",
        r.url,
        (r.recon_data?.contact_info?.emails || []).join("; "),
        (r.recon_data?.contact_info?.phones || []).join("; "),
        (r.recon_data?.contact_info?.urls || []).join("; "),
        r.recon_data?.contact_info?.location || "",
        r.recon_data?.contact_info?.bio || ""
      ]);
      const csv = [header, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      saveAs(blob, `usrlinks_${username}_${Date.now()}.csv`);
    } else if (type === "json") {
      const blob = new Blob([JSON.stringify(scanResults, null, 2)], { type: "application/json" });
      saveAs(blob, `usrlinks_${username}_${Date.now()}.json`);
    } else if (type === "pdf") {
      const doc = new jsPDF();
      doc.text(`USRLINKS Report for "${username}"`, 10, 10);
      const rows = scanResults.map(r => [
        r.platform,
        r.available === true ? "AVAILABLE" : r.available === false ? "TAKEN" : "ERROR",
        r.url,
        (r.recon_data?.contact_info?.emails || []).join("; "),
        (r.recon_data?.contact_info?.phones || []).join("; "),
        (r.recon_data?.contact_info?.urls || []).join("; "),
        r.recon_data?.contact_info?.location || "",
        r.recon_data?.contact_info?.bio || ""
      ]);
      (doc as any).autoTable({
        head: [["Platform", "Status", "URL", "Emails", "Phones", "URLs", "Location", "Bio"]],
        body: rows,
        startY: 20,
        styles: { fontSize: 8 }
      });
      doc.save(`usrlinks_${username}_${Date.now()}.pdf`);
    }
  };

  // Handle platforms file upload
  const handlePlatformsFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setPlatformsFile(e.target.files[0]);
      setSnackbar({ open: true, message: "Custom platforms file loaded", severity: "info" });
    }
  };

  // Simulate live logs for now.
  // Retry failed platforms
  const getFailedPlatforms = () =>
    scanResults.filter(r => r.available === null || r.available === undefined);

  const handleRetryFailed = async () => {
    const failed = getFailedPlatforms();
    if (!failed.length) return;
    setLoading(true);
    addLog("Retrying failed platforms...");
    try {
      // demo 
      const retriedResults = await Promise.all(
        failed.map(async (r) => {
          try {
            const res = await axios.get(`${API_BASE}/check/${encodeURIComponent(username)}`, {
              params: {
                threads: 1,
                deep_scan: deepScan,
                output: "",
                proxy,
                tor,
                generate_dorks: false,
                platforms: "" // not using custom file for retry
              }
            });
            // Find the retried platform in results
            const retried = Array.isArray(res.data)
              ? res.data.find((x: any) => x.platform === r.platform)
              : null;
            return retried || r;
          } catch {
            return r;
          }
        })
      );
      // Merge retried results into scanResults
      setScanResults(results =>
        results.map(r =>
          r.available === null || r.available === undefined
            ? retriedResults.find((x: any) => x.platform === r.platform) || r
            : r
        )
      );
      addLog("Retry complete.");
      setSnackbar({ open: true, message: "Retry complete.", severity: "success" });
    } catch {
      addLog("Retry failed.");
      setSnackbar({ open: true, message: "Retry failed.", severity: "error" });
    }
    setLoading(false);
  };

  // Feedback send logic with error/success snackbar
  const handleFeedbackSend = async () => {
    setAskNameOpen(true);
  };

  // After sending feedback, refresh feedbacks
  const handleSendWithName = async () => {
    setAskNameOpen(false);
    setFeedbackSent(true);
    try {
      const res = await fetch(`${TG_BOT_API}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: feedbackName, message: feedback })
      });
      if (!res.ok) {
        setSnackbar({ open: true, message: "Failed to send feedback.", severity: "error" });
      } else {
        setSnackbar({ open: true, message: "Feedback sent!", severity: "success" });
        fetchFeedbacks(); // Refresh feedbacks after sending
      }
      setFeedback("");
      setFeedbackName("");
    } catch {
      setSnackbar({ open: true, message: "Failed to send feedback.", severity: "error" });
    }
    setTimeout(() => setFeedbackSent(false), 3000);
  };

  // Animation variants for entrance
  const slideUp: Variants = {
    hidden: { opacity: 0, y: 40 },
    visible: (i: number = 1) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.12, duration: 0.6, type: "spring" as const }
    })
  };

  // layout
  return (
    <Box sx={{ minHeight: "100vh", width: "100vw", position: "relative", overflowX: "hidden" }}>
      <AnimatedBackground />

      {/* scan/logbar/results table */}
      <motion.div
        initial="hidden"
        animate="visible"
        // Remove variants here, only use on children
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "flex-start",
          gap: 24,
          zIndex: 1,
          position: "relative",
          paddingLeft: 24,
          paddingRight: 24,
          paddingTop: 32
        }}
      >
        {/* Scan section */}
        <motion.div
          custom={1}
          initial="hidden"
          animate="visible"
          variants={slideUp}
          style={{
            flex: 1,
            minWidth: 320,
            maxWidth: 400,
            backgroundColor: "rgba(10,18,33,0.97)",
            borderRadius: 16,
            boxShadow: "0px 6px 24px rgba(0,0,0,0.3)",
            padding: 24,
            display: "flex",
            flexDirection: "column",
            gap: 16
          }}
        >
          {/* Intro */}
          <Box
            component={motion.div}
            custom={2}
            initial="hidden"
            animate="visible"
            variants={slideUp}
          >
            <Typography variant="h3" sx={{ fontWeight: 900, color: "#00bfff", mb: 1, letterSpacing: 1, display: "flex", alignItems: "center", gap: 1 }}>
              USRLINKS OSINT <AnimatedRadar />
            </Typography>
            <Typography variant="subtitle1" sx={{ color: "#b0c4de", fontWeight: 500 }}>
              Fast, modern username reconnaissance across 30+ platforms.
            </Typography>
          </Box>
          {/* Username input */}
          <TextField
            label="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            variant="filled"
            size="medium"
            sx={{
              bgcolor: "#101c2c",
              borderRadius: 2,
              input: { color: "#fff", fontWeight: 700, fontSize: 20, letterSpacing: 1 }
            }}
            InputLabelProps={{ style: { color: "#b0c4de" } }}
            onKeyDown={e => e.key === "Enter" && handleScan()}
          />
          {/* Toggles */}
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            <FormControlLabel
              control={<Switch checked={deepScan} onChange={e => setDeepScan(e.target.checked)} color="primary" />}
              label="Deep Recon"
              sx={{ color: "#00bfff" }}
            />
            <FormControlLabel
              control={<Switch checked={generateDorks} onChange={e => setGenerateDorks(e.target.checked)} color="primary" />}
              label="Google Dorks"
              sx={{ color: "#00bfff" }}
            />
            <FormControlLabel
              control={<Switch checked={tor} onChange={e => setTor(e.target.checked)} color="primary" />}
              label="Use Tor"
              sx={{ color: "#00bfff" }}
            />
          </Box>
          {/* Proxy/Threads */}
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Proxy"
              value={proxy}
              onChange={e => setProxy(e.target.value)}
              size="small"
              placeholder="http://127.0.0.1:8080"
              variant="filled"
              sx={{ bgcolor: "#101c2c", borderRadius: 2, flex: 1 }}
              InputLabelProps={{ style: { color: "#b0c4de" } }}
            />
            <TextField
              label="Threads"
              type="number"
              value={threads}
              onChange={e => setThreads(Number(e.target.value))}
              size="small"
              inputProps={{ min: 1, max: 50 }}
              variant="filled"
              sx={{ bgcolor: "#101c2c", borderRadius: 2, width: 100 }}
              InputLabelProps={{ style: { color: "#b0c4de" } }}
            />
          </Box>
          {/* Platforms bar */}
          <Box>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                cursor: "pointer",
                bgcolor: "rgba(0,191,255,0.08)",
                borderRadius: 2,
                px: 2,
                py: 1,
                boxShadow: 1,
                mb: 1
              }}
              onClick={() => setPlatformsBarOpen(v => !v)}
            >
              <Typography sx={{ fontWeight: 700, color: "#00bfff", flex: 1 }}>
                Platforms being scanned ({platformsList.length})
              </Typography>
              <IconButton size="small" sx={{ color: "#00bfff" }}>
                {platformsBarOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
              <Tooltip title="Add custom platform">
                <IconButton
                  size="small"
                  sx={{ color: "#00bfff", ml: 1 }}
                  onClick={e => { e.stopPropagation(); }}
                >
                  <AddCircleOutlineIcon />
                </IconButton>
              </Tooltip>
              <TextField
                value={customPlatformInput}
                onChange={e => setCustomPlatformInput(e.target.value)}
                placeholder="Add platform URL"
                size="small"
                sx={{ ml: 1, bgcolor: "#fff", borderRadius: 2, minWidth: 120 }}
                onClick={e => e.stopPropagation()}
                onKeyDown={e => {
                  if (e.key === "Enter") {
                    handleAddCustomPlatform();
                    e.stopPropagation();
                  }
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={e => { e.stopPropagation(); handleAddCustomPlatform(); }}
                      >
                        <SendIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Box>
            {platformsBarOpen && (
              <Paper sx={{ mt: 1, p: 2, bgcolor: "#101c2c", color: "#fff", borderRadius: 2, maxHeight: 200, overflowY: "auto" }}>
                {platformsList.map((p, idx) => (
                  <Box key={idx} sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <Typography sx={{ flex: 1, fontWeight: 600 }}>
                      {p.name}
                      <span style={{ color: "#00bfff", fontWeight: 400, fontSize: 13, marginLeft: 8 }}>{p.url}</span>
                    </Typography>
                    <Switch
                      checked={p.enabled}
                      onChange={() => handleTogglePlatform(idx)}
                      color="primary"
                    />
                    {p.custom && (
                      <IconButton size="small" onClick={() => handleRemoveCustomPlatform(idx)}>
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                ))}
                <Typography variant="caption" color="#00bfff">
                  Toggle platforms to include/exclude from scan. Add more above.
                </Typography>
              </Paper>
            )}
          </Box>
          {/* Scan button */}
          <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleScan}
              disabled={loading}
              sx={{
                px: 6,
                py: 1.5,
                fontWeight: 900,
                fontSize: 22,
                letterSpacing: 2,
                color: "#fff",
                background: "linear-gradient(90deg,#00bfff,#0055ff)",
                boxShadow: "0 0 32px #00bfff, 0 0 8px #0055ff",
                animation: "glow 1.5s infinite alternate"
              }}
            >
              {loading ? <CircularProgress size={28} sx={{ color: "#fff" }} /> : "SCAN"}
            </Button>
            <style>
              {`@keyframes glow { 0% { box-shadow: 0 0 16px #00bfff; } 100% { box-shadow: 0 0 32px #00bfff, 0 0 8px #0055ff; } }`}
            </style>
          </Box>
        </motion.div>

        {/* logbar sec. */}
        <motion.div
          custom={3}
          initial="hidden"
          animate="visible"
          variants={slideUp}
          style={{
            flex: 1,
            minWidth: 340,
            maxWidth: 500,
            backgroundColor: "rgba(15,25,40,0.97)",
            borderRadius: 16,
            boxShadow: "0px 6px 24px rgba(0,0,0,0.3)",
            padding: 24,
            display: "flex",
            flexDirection: "column",
            gap: 16,
            alignItems: "stretch"
          }}
        >
          <Typography variant="h6" sx={{ color: "#00bfff", mb: 1 }}>Scan Logs</Typography>
          <Paper sx={{
            p: 2,
            mb: 2,
            maxHeight: 340,
            minHeight: 240,
            overflow: "auto",
            background: "#16233a",
            fontSize: 16,
            fontFamily: "monospace"
          }}>
            {logs.length === 0
              ? <Typography color="#b0c4de">No logs yet.</Typography>
              : logs.map((log, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: "#b0c4de" }}>{log}</Typography>
                ))
            }
          </Paper>
          {/* Progress bar under logs */}
          <Box sx={{ width: "100%", mb: 2 }}>
            <LinearProgress
              variant={loading ? "indeterminate" : "determinate"}
              value={loading ? undefined : progress}
              sx={{
                height: 12,
                borderRadius: 2,
                background: "#223355",
                "& .MuiLinearProgress-bar": {
                  background: "linear-gradient(90deg,#00bfff,#0055ff)"
                }
              }}
            />
          </Box>
          {/* Leave Feedback under progress bar */}
          <Box sx={{
            bgcolor: "#101c2c",
            borderRadius: 2,
            p: 2,
            mt: 1,
            mb: 1
          }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "#00bfff", mb: 1 }}>
              Leave Feedback
            </Typography>
            <Box sx={{ display: "flex", alignItems: "flex-end", gap: 1 }}>
              <TextareaAutosize
                minRows={2}
                maxRows={8}
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                placeholder="Your message"
                style={{
                  width: 180,
                  borderRadius: 8,
                  background: "#16233a",
                  color: "#fff",
                  border: "1px solid #223355",
                  padding: 8,
                  fontFamily: "inherit",
                  fontSize: 16,
                  resize: "vertical"
                }}
                disabled={feedbackSent}
                onKeyDown={e => {
                  // Prevent Enter from submitting, allow newline
                  if (e.key === "Enter" && !e.shiftKey) {
                    // Do nothing, allow newline
                  }
                }}
              />
              <Button
                variant="contained"
                endIcon={<SendIcon />}
                onClick={handleFeedbackSend}
                disabled={feedbackSent || !feedback.trim()}
                sx={{ bgcolor: "#00bfff", color: "#111", fontWeight: 700, minHeight: 40 }}
              >
                {feedbackSent ? "Sent!" : "Send"}
              </Button>
            </Box>
          </Box>
          {/* Feedbacks from users bar (moved here) */}
          <Box sx={{ width: "100%", mb: 2 }}>
            <Paper
              sx={{
                bgcolor: "#101c2c",
                color: "#b0c4de",
                borderRadius: 2,
                p: 2,
                mb: 2,
                cursor: "pointer",
                boxShadow: 2
              }}
              onClick={() => setFeedbacksOpen(v => !v)}
            >
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Typography sx={{ fontWeight: 700, color: "#00bfff", flex: 1 }}>
                  Feedbacks from users
                </Typography>
                <IconButton size="small" sx={{ color: "#00bfff" }}>
                  {feedbacksOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
              {feedbacksOpen && (
                <Box sx={{ mt: 2 }}>
                  {feedbacks.length === 0 ? (
                    <Typography color="#b0c4de">No feedbacks yet.</Typography>
                  ) : (
                    feedbacks.map((fb, idx) => (
                      <Paper key={idx} sx={{ p: 2, mb: 1, bgcolor: "#16233a" }}>
                        <Typography sx={{ fontWeight: 700, color: "#00bfff" }}>{fb.name}</Typography>
                        <Typography sx={{ color: "#b0c4de" }}>{fb.message}</Typography>
                        {fb.time && (
                          <Typography variant="caption" sx={{ color: "#888" }}>
                            {new Date(fb.time * 1000).toLocaleString()}
                          </Typography>
                        )}
                      </Paper>
                    ))
                  )}
                </Box>
              )}
            </Paper>
          </Box>
        </motion.div>

        {/* results table */}
        <Box
          component={motion.div}
          custom={4}
          initial="hidden"
          animate="visible"
          variants={slideUp}
          sx={{
            flex: 2,
            minWidth: 340,
            maxWidth: 700,
            bgcolor: "rgba(15,25,40,0.97)",
            borderRadius: 4,
            boxShadow: 6,
            p: 3,
            display: "flex",
            flexDirection: "column",
            gap: 2
          }}
        >
          <Typography variant="h6" sx={{ color: "#00bfff", mb: 1 }}>Results</Typography>
          {/* Download buttons */}
          <Box display="flex" gap={2} mb={2}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleDownload("csv")}
              sx={{ color: "#00bfff", borderColor: "#00bfff" }}
            >
              Download CSV
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleDownload("json")}
              sx={{ color: "#00bfff", borderColor: "#00bfff" }}
            >
              Download JSON
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleDownload("pdf")}
              sx={{ color: "#00bfff", borderColor: "#00bfff" }}
            >
              Download PDF
            </Button>
            {getFailedPlatforms().length > 0 && (
              <Button
                variant="contained"
                color="warning"
                onClick={handleRetryFailed}
                disabled={loading}
              >
                Retry Failed Platforms ({getFailedPlatforms().length})
              </Button>
            )}
          </Box>
          {/* Modern results table */}
          {showResults && (
            <Paper sx={{
              bgcolor: "#101c2c",
              borderRadius: 2,
              boxShadow: 2,
              overflowX: "auto"
            }}>
              <table style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: 15,
                color: "#b0c4de"
              }}>
                <thead>
                  <tr style={{ background: "#16233a" }}>
                    <th style={{ padding: 8 }}>Platform</th>
                    <th>Status</th>
                    <th>URL</th>
                    <th>Emails</th>
                    <th>Phones</th>
                    <th>URLs</th>
                    <th>Location</th>
                    <th>Bio</th>
                  </tr>
                </thead>
                <tbody>
                  {scanResults.map((r, idx) => (
                    <tr key={idx} style={{ background: idx % 2 ? "#182a44" : "#101c2c" }}>
                      <td style={{ padding: 8, fontWeight: 600 }}>{r.platform}</td>
                      <td>
                        <Chip
                          label={
                            r.available === true
                              ? "AVAILABLE"
                              : r.available === false
                              ? "TAKEN"
                              : "ERROR"
                          }
                          color={
                            r.available === true
                              ? "success"
                              : r.available === false
                              ? "error"
                              : "warning"
                          }
                          size="small"
                        />
                      </td>
                      <td>
                        <a href={r.url} target="_blank" rel="noopener noreferrer" style={{ color: "#00bfff" }}>
                          {r.url}
                        </a>
                      </td>
                      <td>{(r.recon_data?.contact_info?.emails || []).join(", ")}</td>
                      <td>{(r.recon_data?.contact_info?.phones || []).join(", ")}</td>
                      <td>{(r.recon_data?.contact_info?.urls || []).join(", ")}</td>
                      <td>{r.recon_data?.contact_info?.location || ""}</td>
                      <td>{r.recon_data?.contact_info?.bio || ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Paper>
          )}
          {/* Dorks */}
          {showDorks && (
            <Box>
              <Typography variant="h6" sx={{ color: "#00bfff", mb: 2 }}>Google Dorks</Typography>
              <Paper sx={{ p: 2, background: "#16233a" }}>
                {dorks.map((d, idx) => (
                  <Typography key={idx} variant="body2" sx={{ mb: 1, color: "#b0c4de" }}>
                    <FileCopyIcon fontSize="small" sx={{ verticalAlign: "middle", mr: 1, cursor: "pointer", color: "#00bfff" }}
                      onClick={() => {
                        navigator.clipboard.writeText(d);
                        setSnackbar({ open: true, message: "Copied to clipboard!", severity: "info" });
                      }}
                    />
                    {d}
                  </Typography>
                ))}
              </Paper>
            </Box>
          )}
        </Box>
      </motion.div>

      {/* Footer */}
      <Box
        component={motion.div}
        initial="hidden"
        animate="visible"
        variants={slideUp}
        custom={5}
        sx={{
          width: "100%",
          bgcolor: "#0a1833",
          color: "#b0c4de",
          py: 3,
          px: 4,
          mt: 6,
          borderTop: "2px solid #00bfff",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        {/* Dev info left */}
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "#00bfff" }}>
            Developer Contacts
          </Typography>
          <Box display="flex" alignItems="center" gap={2} mt={1}>
            <Avatar sx={{ bgcolor: "#fff" }}>
              <GitHubIcon sx={{ color: "#333" }} />
            </Avatar>
            <Typography variant="body2" sx={{ color: "#b0c4de" }}>
              <a href="https://github.com/stilla1ex" target="_blank" rel="noopener noreferrer" style={{ color: "#b0c4de", textDecoration: "none" }}>
                stilla1ex
              </a>
            </Typography>
            <Avatar sx={{ bgcolor: "#fff" }}>
              <GitHubIcon sx={{ color: "#333" }} />
            </Avatar>
            <Typography variant="body2" sx={{ color: "#b0c4de" }}>
              <a href="https://github.com/max5010cs" target="_blank" rel="noopener noreferrer" style={{ color: "#b0c4de", textDecoration: "none" }}>
                max5010cs
              </a>
            </Typography>
            <Avatar sx={{ bgcolor: "#111" }}>
              <TwitterIcon sx={{ color: "#1da1f2" }} />
            </Avatar>
            <Typography variant="body2" sx={{ color: "#b0c4de" }}>
              <a href="https://x.com/stilla1ex" target="_blank" rel="noopener noreferrer" style={{ color: "#b0c4de", textDecoration: "none" }}>
                @stilla1ex
              </a>
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Name dialog for feedback */}
      <Dialog open={askNameOpen} onClose={() => setAskNameOpen(false)} PaperProps={{
        sx: { bgcolor: "rgba(10,18,33,0.97)", borderRadius: 3, color: "#fff", minWidth: 320 }
      }}>
        <DialogTitle sx={{ color: "#00bfff", fontWeight: 700, textAlign: "center" }}>
          Enter your name
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            label="Name"
            value={feedbackName}
            onChange={e => setFeedbackName(e.target.value)}
            fullWidth
            sx={{ mt: 2, bgcolor: "#16233a", borderRadius: 2 }}
            InputLabelProps={{ style: { color: "#b0c4de" } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAskNameOpen(false)} sx={{ color: "#b0c4de" }}>Cancel</Button>
          <Button
            onClick={handleSendWithName}
            disabled={!feedbackName.trim()}
            sx={{ bgcolor: "#00bfff", color: "#111", fontWeight: 700 }}
          >
            Send
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
