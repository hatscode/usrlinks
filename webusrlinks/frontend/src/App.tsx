import React, { useState, useRef } from "react";
import {
  Container, Box, Typography, TextField, Button, Switch, FormControlLabel,
  Paper, CircularProgress, Snackbar, Alert, AppBar, Toolbar, IconButton, Tooltip,
  Menu, MenuItem, Select, InputLabel, FormControl, Chip, LinearProgress
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import axios from "axios";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { saveAs } from "file-saver";

// Animated background (simple particles)
const AnimatedBackground = () => (
  <div style={{
    position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh",
    zIndex: -1, background: "radial-gradient(circle at 20% 30%, #0ff 0%, #222 100%)",
    animation: "bgmove 10s infinite alternate"
  }}>
    <style>
      {`@keyframes bgmove {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
      }`}
    </style>
  </div>
);

const API_BASE = "http://localhost:8080";

const defaultThreads = 10;

const outputOptions = [
  { value: "", label: "None" },
  { value: "csv", label: "CSV" },
  { value: "json", label: "JSON" }
];

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
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // Handle scan
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
      // If platforms file is provided, upload it first
      if (platformsFile) {
        const formData = new FormData();
        formData.append("file", platformsFile);
        await axios.post(`${API_BASE}/upload_platforms`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      }

      const res = await axios.get(`${API_BASE}/check/${encodeURIComponent(username)}`, { params });
      if (generateDorks) {
        setDorks(res.data.dorks || []);
        setShowDorks(true);
      } else {
        setScanResults(res.data);
        setShowResults(true);
      }
      setSnackbar({ open: true, message: "Scan complete!", severity: "success" });
    } catch (e: any) {
      setSnackbar({ open: true, message: "Scan failed: " + (e?.message || "Unknown error"), severity: "error" });
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

  // UI
  return (
    <Box>
      <AnimatedBackground />
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar>
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: 2 }}>
            USRLINKS <span style={{ color: "#00e6e6" }}>OSINT</span>
          </Typography>
          <Tooltip title="Supported Platforms">
            <IconButton color="primary" onClick={fetchPlatforms}>
              <InfoIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton color="primary" onClick={e => setAnchorEl(e.currentTarget)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}>
            <MenuItem>
              <FormControlLabel
                control={<Switch checked={tor} onChange={e => setTor(e.target.checked)} />}
                label="Use Tor"
              />
            </MenuItem>
            <MenuItem>
              <TextField
                label="Proxy"
                value={proxy}
                onChange={e => setProxy(e.target.value)}
                size="small"
                fullWidth
                placeholder="http://127.0.0.1:8080"
              />
            </MenuItem>
            <MenuItem>
              <TextField
                label="Threads"
                type="number"
                value={threads}
                onChange={e => setThreads(Number(e.target.value))}
                size="small"
                inputProps={{ min: 1, max: 50 }}
                fullWidth
              />
            </MenuItem>
            <MenuItem>
              <FormControl fullWidth>
                <InputLabel>Output</InputLabel>
                <Select
                  value={output}
                  label="Output"
                  onChange={e => setOutput(e.target.value)}
                >
                  {outputOptions.map(opt => (
                    <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </MenuItem>
            <MenuItem>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                startIcon={<FileCopyIcon />}
              >
                Upload Platforms JSON
                <input
                  type="file"
                  accept=".json"
                  hidden
                  ref={fileInputRef}
                  onChange={handlePlatformsFile}
                />
              </Button>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 6, mb: 6 }}>
        <Paper elevation={6} sx={{ p: 4, borderRadius: 4, background: "rgba(255,255,255,0.95)" }}>
          <Typography variant="h4" align="center" gutterBottom fontWeight={700}>
            Username OSINT Scanner
          </Typography>
          <Typography align="center" color="text.secondary" sx={{ mb: 2 }}>
            Scan 30+ platforms for username availability, deep recon, and more.
          </Typography>
          <Box display="flex" gap={2} alignItems="center" justifyContent="center" mb={2}>
            <TextField
              label="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              variant="outlined"
              size="medium"
              sx={{ minWidth: 200 }}
              onKeyDown={e => e.key === "Enter" && handleScan()}
            />
            <FormControlLabel
              control={<Switch checked={deepScan} onChange={e => setDeepScan(e.target.checked)} />}
              label="Deep Recon"
            />
            <FormControlLabel
              control={<Switch checked={generateDorks} onChange={e => setGenerateDorks(e.target.checked)} />}
              label="Google Dorks"
            />
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleScan}
              disabled={loading}
              sx={{ px: 4, fontWeight: 700, boxShadow: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : "Scan"}
            </Button>
          </Box>
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          {logs.length > 0 && (
            <Paper sx={{ p: 2, mb: 2, maxHeight: 200, overflow: "auto", background: "#f5f5f5" }}>
              <Typography variant="subtitle2" color="text.secondary">Logs:</Typography>
              {logs.map((log, idx) => (
                <Typography key={idx} variant="body2">{log}</Typography>
              ))}
            </Paper>
          )}
          {showResults && (
            <Box>
              <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Results</Typography>
              <Box sx={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 16 }}>
                  <thead>
                    <tr style={{ background: "#e0f7fa" }}>
                      <th>Platform</th>
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
                      <tr key={idx} style={{ background: idx % 2 ? "#fafafa" : "#fff" }}>
                        <td>{r.platform}</td>
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
                          <a href={r.url} target="_blank" rel="noopener noreferrer">
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
              </Box>
              <Box display="flex" gap={2} mb={2}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownload("csv")}
                >
                  Download CSV
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownload("json")}
                >
                  Download JSON
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownload("pdf")}
                >
                  Download PDF
                </Button>
              </Box>
            </Box>
          )}
          {showDorks && (
            <Box>
              <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Google Dorks</Typography>
              <Paper sx={{ p: 2, background: "#f5f5f5" }}>
                {dorks.map((d, idx) => (
                  <Typography key={idx} variant="body2" sx={{ mb: 1 }}>
                    <FileCopyIcon fontSize="small" sx={{ verticalAlign: "middle", mr: 1, cursor: "pointer" }}
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
        </Paper>
      </Container>

      {/* Platforms Modal */}
      {showPlatforms && (
        <Box
          sx={{
            position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh",
            bgcolor: "rgba(0,0,0,0.5)", zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center"
          }}
          onClick={() => setShowPlatforms(false)}
        >
          <Paper sx={{ p: 4, minWidth: 400, maxHeight: "80vh", overflow: "auto" }} onClick={e => e.stopPropagation()}>
            <Typography variant="h6" gutterBottom>Supported Platforms</Typography>
            <ul>
              {Object.keys(platforms).map((name, idx) => (
                <li key={idx}>
                  <b>{name}</b> {platforms[name].recon_enabled ? <Chip label="Recon" color="success" size="small" /> : null}
                </li>
              ))}
            </ul>
            <Button variant="contained" onClick={() => setShowPlatforms(false)} sx={{ mt: 2 }}>Close</Button>
          </Paper>
        </Box>
      )}

      {/* Snackbar for notifications */}
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
