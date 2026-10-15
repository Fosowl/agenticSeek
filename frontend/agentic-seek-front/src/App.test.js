import { act, fireEvent, render, screen } from "@testing-library/react";
import axios from "axios";
import App from "./App";
import { TOKEN_STORAGE_KEY } from "./apiAuth";
import { ThemeProvider } from "./contexts/ThemeContext";

// Jest 27 ignores package "exports", so load the CommonJS builds directly.
jest.mock("axios", () => jest.requireActual("axios/dist/node/axios.cjs"));
jest.mock("react-markdown", () => ({ children }) => children);

const GOOD_TOKEN = "good-token";
let requests = [];

const reply = (config, status, data) => {
  const response = { data, status, statusText: "", headers: {}, config };
  if (status < 400) return Promise.resolve(response);
  return Promise.reject(
    new axios.AxiosError("Request failed", "ERR_BAD_REQUEST", config, null, response)
  );
};

// Fake backend: /health is public, everything else needs GOOD_TOKEN.
const fakeBackend = (config) => {
  // REACT_APP_BACKEND_URL is unset in tests, so keep only the last segment.
  const path = `/${config.url.split("?")[0].split("/").pop()}`;
  const auth = config.headers.get("Authorization");
  requests.push({ path, auth });
  if (path.endsWith("/health")) return reply(config, 200, { status: "healthy" });
  if (auth !== `Bearer ${GOOD_TOKEN}`) return reply(config, 401, { detail: "Unauthorized" });
  if (path.endsWith("/screenshot")) return reply(config, 404, { error: "none" });
  return reply(config, 200, { answer: "", blocks: {}, done: false, status: "ok" });
};

const tick = () =>
  act(async () => {
    jest.advanceTimersByTime(3000);
  });

const enterToken = (token) => {
  fireEvent.change(screen.getByLabelText("API token"), { target: { value: token } });
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
};

beforeEach(() => {
  jest.useFakeTimers();
  localStorage.clear();
  requests = [];
  axios.defaults.adapter = fakeBackend;
});

afterEach(() => {
  jest.useRealTimers();
});

test("asks for the API token on 401, pauses polling, and retries with it", async () => {
  render(
    <ThemeProvider>
      <App />
    </ThemeProvider>
  );

  await tick();
  expect(await screen.findByText("API token required")).toBeInTheDocument();

  requests = [];
  await tick();
  expect(requests.map((r) => r.path)).toEqual(["/health"]);

  enterToken("wrong-token");
  expect(await screen.findByRole("alert")).toHaveTextContent(/rejected/);
  expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe("wrong-token");

  requests = [];
  enterToken(GOOD_TOKEN);
  await tick();
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe(GOOD_TOKEN);
  const latest = requests.filter((r) => r.path === "/latest_answer");
  expect(latest.length).toBeGreaterThan(0);
  latest.forEach((r) => expect(r.auth).toBe(`Bearer ${GOOD_TOKEN}`));
});
