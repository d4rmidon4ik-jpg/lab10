package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPingHandler(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/ping", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var resp PingResponse
	assert.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "pong", resp.Message)
	assert.Equal(t, "ok", resp.Status)
}

func TestCalculateHandler_Add(t *testing.T) {
	r := setupRouter()
	body := `{"a":3,"b":4,"op":"add"}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/calculate", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var resp CalculateResponse
	assert.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, 7.0, resp.Result)
	assert.Equal(t, "add", resp.Op)
}

func TestCalculateHandler_Sub(t *testing.T) {
	r := setupRouter()
	body := `{"a":10,"b":3,"op":"sub"}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/calculate", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var resp CalculateResponse
	assert.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, 7.0, resp.Result)
}

func TestCalculateHandler_DivisionByZero(t *testing.T) {
	r := setupRouter()
	body := `{"a":5,"b":0,"op":"div"}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/calculate", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnprocessableEntity, w.Code)
	var resp ErrorResponse
	assert.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "division by zero", resp.Error)
}

func TestCalculateHandler_InvalidOp(t *testing.T) {
	r := setupRouter()
	body := `{"a":5,"b":2,"op":"pow"}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/calculate", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestCalculateHandler_MissingFields(t *testing.T) {
	r := setupRouter()
	body := `{"a":5}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/calculate", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestGetItemHandler_Valid(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/items/42", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var resp ItemResponse
	assert.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, 42, resp.ID)
	assert.NotEmpty(t, resp.Name)
}

func TestGetItemHandler_InvalidID(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/items/abc", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestGetItemHandler_NegativeID(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/items/-5", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

func TestGetItemHandler_ZeroID(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/items/0", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}