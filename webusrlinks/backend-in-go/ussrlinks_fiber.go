package main

import (
	"bytes"
	"crypto/md5"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"golang.org/x/net/proxy"
)

type Platform struct {
	URL          string   `json:"url"`
	Method       string   `json:"method"`
	Code         []int    `json:"code,omitempty"`
	ErrorMsg     []string `json:"error_msg,omitempty"`
	ReconEnabled bool     `json:"recon_enabled,omitempty"`
	ApiEndpoint  string   `json:"api_endpoint,omitempty"`
}

type ReconContact struct {
	Emails   []string `json:"emails"`
	Phones   []string `json:"phones"`
	URLs     []string `json:"urls"`
	Location string   `json:"location,omitempty"`
	Bio      string   `json:"bio,omitempty"`
	Name     string   `json:"name,omitempty"`
	Verified bool     `json:"verified,omitempty"`
}

type ReconImage struct {
	URL        string `json:"url,omitempty"`
	Hash       string `json:"hash,omitempty"`
	Downloaded bool   `json:"downloaded,omitempty"`
}

type ReconData struct {
	ContactInfo  ReconContact `json:"contact_info"`
	ProfileImage ReconImage   `json:"profile_image"`
}

type ScanResult struct {
	Platform  string    `json:"platform"`
	URL       string    `json:"url"`
	Available *bool     `json:"available"`
	Error     string    `json:"error,omitempty"`
	ReconData ReconData `json:"recon_data"`
}

var platforms = map[string]Platform{
	"GitHub": {
		URL:          "https://github.com/%s",
		Method:       "status_code",
		Code:         []int{404},
		ReconEnabled: true,
		ApiEndpoint:  "https://api.github.com/users/%s",
	},
	"Twitter": {
		URL:          "https://twitter.com/%s",
		Method:       "response_text",
		ErrorMsg:     []string{"doesn't exist", "404"},
		ReconEnabled: true,
	},
	"Instagram": {
		URL:          "https://instagram.com/%s",
		Method:       "status_code",
		Code:         []int{404},
		ReconEnabled: true,
	},
	"Reddit": {
		URL:          "https://reddit.com/user/%s",
		Method:       "status_code",
		Code:         []int{404},
		ReconEnabled: true,
	},
	"LinkedIn": {
		URL:          "https://linkedin.com/in/%s",
		Method:       "status_code",
		Code:         []int{404},
		ReconEnabled: true,
	},
	"TikTok": {
		URL:      "https://tiktok.com/@%s",
		Method:   "response_text",
		ErrorMsg: []string{"Couldn't find this account"},
	},
	"YouTube": {
		URL:      "https://youtube.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"This channel does not exist"},
	},
	"Twitch": {
		URL:    "https://twitch.tv/%s",
		Method: "status_code",
		Code:   []int{404},
	},
	"Facebook": {
		URL:      "https://facebook.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"This page isn't available"},
	},
	"Pinterest": {
		URL:      "https://pinterest.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Sorry, we couldn't find that page"},
	},
	"Steam": {
		URL:      "https://steamcommunity.com/id/%s",
		Method:   "response_text",
		ErrorMsg: []string{"The specified profile could not be found"},
	},
	"Vimeo": {
		URL:      "https://vimeo.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Sorry, we couldn't find that user"},
	},
	"SoundCloud": {
		URL:      "https://soundcloud.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Oops! We can't find that track"},
	},
	"Medium": {
		URL:      "https://medium.com/@%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"DeviantArt": {
		URL:      "https://%s.deviantart.com",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"GitLab": {
		URL:    "https://gitlab.com/%s",
		Method: "status_code",
		Code:   []int{404},
	},
	"Bitbucket": {
		URL:    "https://bitbucket.org/%s",
		Method: "status_code",
		Code:   []int{404},
	},
	"Keybase": {
		URL:    "https://keybase.io/%s",
		Method: "status_code",
		Code:   []int{404},
	},
	"HackerNews": {
		URL:      "https://news.ycombinator.com/user?id=%s",
		Method:   "response_text",
		ErrorMsg: []string{"No such user"},
	},
	"CodePen": {
		URL:      "https://codepen.io/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Sorry, couldn't find that pen"},
	},
	"Telegram": {
		URL:      "https://t.me/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Telegram channel not found"},
	},
	"Tumblr": {
		URL:      "https://%s.tumblr.com",
		Method:   "response_text",
		ErrorMsg: []string{"Nothing here"},
	},
	"Spotify": {
		URL:      "https://open.spotify.com/user/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Couldn't find that user"},
	},
	"Last.fm": {
		URL:      "https://last.fm/user/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Page not found"},
	},
	"Roblox": {
		URL:      "https://www.roblox.com/user.aspx?username=%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"Quora": {
		URL:      "https://www.quora.com/profile/%s",
		Method:   "response_text",
		ErrorMsg: []string{"Oops! The page you were looking for doesn't exist"},
	},
	"VK": {
		URL:      "https://vk.com/%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"Imgur": {
		URL:      "https://imgur.com/user/%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"Etsy": {
		URL:      "https://www.etsy.com/shop/%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
	"Pastebin": {
		URL:      "https://pastebin.com/u/%s",
		Method:   "response_text",
		ErrorMsg: []string{"404"},
	},
}

var (
	emailRegex = regexp.MustCompile(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`)
	phoneRegex = regexp.MustCompile(`\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}`)
	urlRegex   = regexp.MustCompile(`https?://[^\s]+`)
)

// Proxy/Tor support
func getClient(proxyAddr string, tor bool) *http.Client {
	if proxyAddr != "" || tor {
		var dialer proxy.Dialer
		var err error
		if tor {
			dialer, err = proxy.SOCKS5("tcp", "127.0.0.1:9050", nil, proxy.Direct)
		} else {
			dialer, err = proxy.SOCKS5("tcp", proxyAddr, nil, proxy.Direct)
		}
		if err != nil {
			return &http.Client{Timeout: 15 * time.Second}
		}
		transport := &http.Transport{
			Dial: dialer.Dial,
		}
		return &http.Client{Transport: transport, Timeout: 15 * time.Second}
	}
	return &http.Client{Timeout: 15 * time.Second}
}

// Recon logic
func extractContactInfo(doc *goquery.Document, url string) ReconContact {
	text := doc.Text()
	emails := emailRegex.FindAllString(text, -1)
	phones := phoneRegex.FindAllString(text, -1)
	urls := urlRegex.FindAllString(text, -1)
	contact := ReconContact{
		Emails: emails,
		Phones: phones,
		URLs:   urls,
	}
	// Platform-specific extraction
	if strings.Contains(url, "github.com") {
		bio := doc.Find("div.user-profile-bio").Text()
		if bio != "" {
			contact.Bio = strings.TrimSpace(bio)
		}
		location := doc.Find("li[itemprop='homeLocation']").Text()
		if location != "" {
			contact.Location = strings.TrimSpace(location)
		}
		name := doc.Find("span[itemprop='name']").Text()
		if name != "" {
			contact.Name = strings.TrimSpace(name)
		}
	}
	if strings.Contains(url, "twitter.com") || strings.Contains(url, "x.com") {
		bio := doc.Find("div[data-testid='UserDescription']").Text()
		if bio != "" {
			contact.Bio = strings.TrimSpace(bio)
		}
		location := doc.Find("span[data-testid='UserLocation']").Text()
		if location != "" {
			contact.Location = strings.TrimSpace(location)
		}
		verified := doc.Find("svg[data-testid='verificationBadge']").Length() > 0
		contact.Verified = verified
	}
	if strings.Contains(url, "instagram.com") {
		bio := doc.Find("meta[property='og:description']").AttrOr("content", "")
		if bio != "" {
			contact.Bio = strings.TrimSpace(bio)
		}
	}
	if strings.Contains(url, "linkedin.com") {
		location := doc.Find("span.text-body-small").Text()
		if location != "" && strings.Contains(strings.ToLower(location), "location") {
			contact.Location = strings.TrimSpace(location)
		}
	}
	return contact
}

func extractProfileImage(doc *goquery.Document, url string) ReconImage {
	var imgURL string
	selectors := []string{
		"img[data-testid='userAvatarImage']",
		".avatar img",
		"img[alt*='profile']",
		"img[class*='avatar']",
		"img[class*='profile']",
	}
	for _, sel := range selectors {
		img := doc.Find(sel)
		if img.Length() > 0 {
			imgURL, _ = img.Attr("src")
			break
		}
	}
	if imgURL == "" {
		return ReconImage{}
	}
	// Download and hash image
	resp, err := http.Get(imgURL)
	if err == nil && resp.StatusCode == 200 {
		defer resp.Body.Close()
		data, err := io.ReadAll(resp.Body)
		if err == nil {
			hash := fmt.Sprintf("%x", md5.Sum(data))
			return ReconImage{URL: imgURL, Hash: hash, Downloaded: true}
		}
	}
	return ReconImage{URL: imgURL}
}

// Google dorks
func generateGoogleDorks(username string) []string {
	return []string{
		fmt.Sprintf(`"%s"`, username),
		fmt.Sprintf(`"%s" site:pastebin.com`, username),
		fmt.Sprintf(`"%s" site:github.com`, username),
		fmt.Sprintf(`"%s" site:reddit.com`, username),
		fmt.Sprintf(`"%s" filetype:pdf`, username),
		fmt.Sprintf(`"%s" "email" OR "contact"`, username),
		fmt.Sprintf(`"%s" "phone" OR "mobile"`, username),
		fmt.Sprintf(`"%s" inurl:resume OR inurl:cv`, username),
		fmt.Sprintf(`intitle:"%s"`, username),
		fmt.Sprintf(`"%s" site:linkedin.com`, username),
	}
}

// Scan logic with retries
func scanPlatform(username string, platformName string, platform Platform, client *http.Client, deepScan bool) ScanResult {
	url := fmt.Sprintf(platform.URL, username)
	result := ScanResult{
		Platform: platformName,
		URL:      url,
	}
	// Add this log for debugging
	if logger != nil {
		logger.Printf("Scanning %s: %s", platformName, url)
	}
	var resp *http.Response
	var err error
	for attempt := 0; attempt < 3; attempt++ {
		req, reqErr := http.NewRequest("GET", url, nil)
		if reqErr != nil {
			err = reqErr
			time.Sleep(time.Second * time.Duration(attempt+1))
			continue
		}
		req.Header.Set("User-Agent", getRandomUserAgent())
		resp, err = client.Do(req)
		if err == nil {
			break
		}
		time.Sleep(time.Second * time.Duration(attempt+1))
	}
	if err != nil {
		result.Available = nil
		result.Error = err.Error()
		return result
	}
	defer resp.Body.Close()
	var available bool
	if platform.Method == "status_code" {
		for _, code := range platform.Code {
			if resp.StatusCode == code {
				available = true
				break
			}
		}
		result.Available = &available
	} else if platform.Method == "response_text" {
		bodyBytes, _ := io.ReadAll(resp.Body)
		bodyStr := strings.ToLower(string(bodyBytes))
		for _, msg := range platform.ErrorMsg {
			if strings.Contains(bodyStr, strings.ToLower(msg)) {
				available = true
				break
			}
		}
		result.Available = &available
		resp.Body = io.NopCloser(bytes.NewReader(bodyBytes))
	} else {
		result.Available = nil
	}
	// Recon if taken
	if result.Available != nil && !*result.Available && platform.ReconEnabled && deepScan {
		doc, err := goquery.NewDocumentFromReader(resp.Body)
		if err == nil {
			result.ReconData.ContactInfo = extractContactInfo(doc, url)
			result.ReconData.ProfileImage = extractProfileImage(doc, url)
		}
	}
	return result
}

func scanUsernames(username string, proxy string, tor bool, threads int, deepScan bool) []ScanResult {
	client := getClient(proxy, tor)
	var wg sync.WaitGroup
	resultsChan := make(chan ScanResult, len(platforms))
	keys := make([]string, 0, len(platforms))
	for k := range platforms {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, name := range keys {
		wg.Add(1)
		go func(name string) {
			defer wg.Done()
			res := scanPlatform(username, name, platforms[name], client, deepScan)
			resultsChan <- res
		}(name)
	}
	wg.Wait()
	close(resultsChan)
	var results []ScanResult
	for res := range resultsChan {
		results = append(results, res)
	}
	return results
}

// --- 10. User-Agent randomization ---
var userAgents = []string{
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

func getRandomUserAgent() string {
	return userAgents[rand.Intn(len(userAgents))]
}

// --- 5. Custom platform config (load from JSON) ---
func loadPlatforms(configPath string) map[string]Platform {
	if configPath != "" {
		f, err := os.Open(configPath)
		if err == nil {
			defer f.Close()
			var custom map[string]Platform
			if err := json.NewDecoder(f).Decode(&custom); err == nil {
				return custom
			}
		}
	}
	return platforms
}

// --- 11. Logging to file ---
var logger *log.Logger

func setupLogger() {
	logFile, err := os.OpenFile("usrlinks_backend.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err == nil {
		logger = log.New(logFile, "", log.LstdFlags)
	}
}

// --- 4. Saving results to file (CSV/JSON) ---
func saveResultsToFile(results []ScanResult, username, format string) error {
	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("USRLINKS_%s_%s.%s", username, timestamp, format)
	if format == "csv" {
		f, err := os.Create(filename)
		if err != nil {
			return err
		}
		defer f.Close()
		w := csv.NewWriter(f)
		w.Write([]string{"Platform", "Status", "URL", "Emails", "Phones", "URLs", "Location", "Bio"})
		for _, r := range results {
			status := "ERROR"
			if r.Available != nil && *r.Available {
				status = "AVAILABLE"
			}
			if r.Available != nil && !*r.Available {
				status = "TAKEN"
			}
			emails := strings.Join(r.ReconData.ContactInfo.Emails, "; ")
			phones := strings.Join(r.ReconData.ContactInfo.Phones, "; ")
			urls := strings.Join(r.ReconData.ContactInfo.URLs, "; ")
			location := r.ReconData.ContactInfo.Location
			bio := r.ReconData.ContactInfo.Bio
			w.Write([]string{r.Platform, status, r.URL, emails, phones, urls, location, bio})
		}
		w.Flush()
		return nil
	} else if format == "json" {
		f, err := os.Create(filename)
		if err != nil {
			return err
		}
		defer f.Close()
		return json.NewEncoder(f).Encode(results)
	}
	return fmt.Errorf("unsupported format")
}

// --- 3. Retry failed platforms after scan ---
func retryFailedPlatforms(results []ScanResult, username string, proxy string, tor bool, threads int, deepScan bool, platforms map[string]Platform) []ScanResult {
	failed := []ScanResult{}
	for _, r := range results {
		if r.Available == nil {
			failed = append(failed, r)
		}
	}
	if len(failed) == 0 {
		return results
	}
	client := getClient(proxy, tor)
	for attempt := 0; attempt < 2; attempt++ {
		newFailed := []ScanResult{}
		for _, fr := range failed {
			res := scanPlatform(username, fr.Platform, platforms[fr.Platform], client, deepScan)
			if res.Available == nil {
				newFailed = append(newFailed, res)
			} else {
				// Replace in results
				for i := range results {
					if results[i].Platform == fr.Platform {
						results[i] = res
					}
				}
			}
		}
		if len(newFailed) == 0 {
			break
		}
		failed = newFailed
	}
	return results
}

var scanStatus = struct {
	sync.RWMutex
	Status map[string]string
}{Status: make(map[string]string)}

func scanUsernamesWithPool(username string, proxy string, tor bool, threads int, deepScan bool, platforms map[string]Platform) []ScanResult {
	client := getClient(proxy, tor)
	type job struct{ name string }
	type result struct{ scan ScanResult }
	jobs := make(chan job, len(platforms))
	resultsChan := make(chan result, len(platforms))
	for w := 0; w < threads; w++ {
		go func() {
			for j := range jobs {
				r := scanPlatform(username, j.name, platforms[j.name], client, deepScan)
				resultsChan <- result{r}
			}
		}()
	}
	keys := make([]string, 0, len(platforms))
	for k := range platforms {
		keys = append(keys, k)
	}
	for _, name := range keys {
		jobs <- job{name}
	}
	close(jobs)
	var results []ScanResult
	for i := 0; i < len(keys); i++ {
		r := <-resultsChan
		results = append(results, r.scan)
	}
	return results
}

// --- Main Fiber endpoints ---
func main() {
	setupLogger()
	app := fiber.New()

	// Enable CORS for frontend requests
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	// --- Progress status endpoint ---
	app.Get("/status/:scanid", func(c *fiber.Ctx) error {
		scanid := c.Params("scanid")
		scanStatus.RLock()
		status := scanStatus.Status[scanid]
		scanStatus.RUnlock()
		return c.JSON(fiber.Map{"scanid": scanid, "status": status})
	})

	app.Get("/check/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		proxy := c.Query("proxy")
		tor, _ := strconv.ParseBool(c.Query("tor"))
		threads, _ := strconv.Atoi(c.Query("threads"))
		if threads <= 0 {
			threads = 10
		}
		deepScan, _ := strconv.ParseBool(c.Query("deep_scan"))
		output := c.Query("output")
		generateDorks, _ := strconv.ParseBool(c.Query("generate_dorks"))
		platformsConfig := c.Query("platforms")
		scanid := fmt.Sprintf("%s_%d", username, time.Now().UnixNano())

		platformsToUse := loadPlatforms(platformsConfig)

		if generateDorks {
			dorks := generateGoogleDorks(username)
			return c.JSON(fiber.Map{"dorks": dorks})
		}

		scanStatus.Lock()
		scanStatus.Status[scanid] = "Scanning"
		scanStatus.Unlock()

		var results []ScanResult
		if threads > 1 {
			results = scanUsernamesWithPool(username, proxy, tor, threads, deepScan, platformsToUse)
		} else {
			results = scanUsernames(username, proxy, tor, threads, deepScan)
		}

		// --- Retry failed platforms after scan ---
		results = retryFailedPlatforms(results, username, proxy, tor, threads, deepScan, platformsToUse)

		scanStatus.Lock()
		scanStatus.Status[scanid] = "Completed"
		scanStatus.Unlock()

		// --- Logging to file ---
		if logger != nil {
			logger.Printf("Scan for %s completed. %d results.", username, len(results))
		}

		// --- Save results to file if requested ---
		if output == "csv" || output == "json" {
			if err := saveResultsToFile(results, username, output); err != nil {
				if logger != nil {
					logger.Printf("Error saving results: %v", err)
				}
			}
		}

		if output == "csv" {
			b := &bytes.Buffer{}
			w := csv.NewWriter(b)
			w.Write([]string{"Platform", "Status", "URL", "Emails", "Phones", "URLs", "Location", "Bio"})
			for _, r := range results {
				status := "ERROR"
				if r.Available != nil && *r.Available {
					status = "AVAILABLE"
				}
				if r.Available != nil && !*r.Available {
					status = "TAKEN"
				}
				emails := strings.Join(r.ReconData.ContactInfo.Emails, "; ")
				phones := strings.Join(r.ReconData.ContactInfo.Phones, "; ")
				urls := strings.Join(r.ReconData.ContactInfo.URLs, "; ")
				location := r.ReconData.ContactInfo.Location
				bio := r.ReconData.ContactInfo.Bio
				w.Write([]string{r.Platform, status, r.URL, emails, phones, urls, location, bio})
			}
			w.Flush()
			c.Set("Content-Type", "text/csv")
			return c.Send(b.Bytes())
		}
		// Defensive: catch JSON marshal errors
		resp, err := json.Marshal(results)
		if err != nil {
			if logger != nil {
				logger.Printf("JSON marshal error: %v", err)
			}
			return c.Status(500).JSON(fiber.Map{"error": "Failed to encode results"})
		}
		c.Set("Content-Type", "application/json")
		return c.Send(resp)
	})

	app.Get("/dorks/:username", func(c *fiber.Ctx) error {
		username := c.Params("username")
		dorks := generateGoogleDorks(username)
		return c.JSON(fiber.Map{"dorks": dorks})
	})

	app.Get("/platforms", func(c *fiber.Ctx) error {
		return c.JSON(platforms)
	})

	// --- Feedback endpoint ---
	app.Post("/feedback", func(c *fiber.Ctx) error {
		var req struct {
			Name    string `json:"name"`
			Message string `json:"message"`
		}
		if err := c.BodyParser(&req); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid request"})
		}
		if req.Name == "" || req.Message == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Name and message required"})
		}
		err := sendTelegramFeedback(req.Name, req.Message)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(fiber.Map{"status": "ok"})
	})

	fmt.Println("USRLINKS Fiber backend running on :8080")
	app.Listen("0.0.0.0:8080")
}

// Send feedback to Telegram bot using bot token and chat ID from env
func sendTelegramFeedback(name, message string) error {
	botToken := os.Getenv("TG_BOT_TOKEN")
	chatID := os.Getenv("TG_BOT_CHAT_ID") // Numeric Telegram user ID
	if botToken == "" || chatID == "" {
		return fmt.Errorf("telegram bot token or chat ID not set")
	}
	text := fmt.Sprintf("*Feedback from %s:*\n%s", name, message)
	url := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", botToken)
	payload := map[string]interface{}{
		"chat_id":    chatID,
		"text":       text,
		"parse_mode": "Markdown",
	}
	body, _ := json.Marshal(payload)
	resp, err := http.Post(url, "application/json", bytes.NewReader(body))
	if err != nil {
		if logger != nil {
			logger.Printf("Telegram POST error: %v", err)
		}
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		respBody, _ := io.ReadAll(resp.Body)
		errMsg := fmt.Sprintf("telegram API error: %s - %s", resp.Status, string(respBody))
		if logger != nil {
			logger.Printf("Telegram API error: %s", errMsg)
		}
		return fmt.Errorf("%s", errMsg)
	}
	return nil
}

// 1. Terminal UI & Styling
// Not relevant for web backend. Fiber returns JSON/CSV, not colored terminal output.

// 2. Progress Bar / Status Updates
// Not implemented. Fiber is stateless HTTP; for live progress, use WebSocket/SSE.

// 3. Retry failed platforms after scan
// Only per-request retries are implemented. No post-scan retry for failed platforms.

// 4. Saving results to file (CSV/JSON)
// Implemented. Results can be saved to CSV or JSON file.

// 5. Custom platform config (load from JSON)
// Implemented. Platforms can be loaded from a custom JSON file.

// 6. Listing supported platforms
// Implemented as `/platforms` endpoint.

// 7. Deep Reconnaissance (all platforms)
// Partially implemented. Some platform-specific recon logic may be less robust than Python’s BeautifulSoup.

// 8. Google Dorks Generation
// Implemented as `/dorks/:username` and query param.

// 9. Thread/concurrency control
// Goroutines are used, but threads param is not strictly enforced (no worker pool).

// 10. User-Agent randomization
// Implemented. Requests use a random User-Agent from a predefined list.

// 11. Logging to file
// Implemented. Logs are written to `usrlinks_backend.log` file.

// 12. Error handling/logging
// Partial. Errors are returned in JSON, not logged to file.

// 13. CLI arguments
// Not relevant for web backend. Use HTTP query params.
