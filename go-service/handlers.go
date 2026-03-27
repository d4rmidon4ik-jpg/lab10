package main

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// PingResponse описывает ответ /ping
type PingResponse struct {
	Message string `json:"message"`
	Status  string `json:"status"`
}

// CalculateRequest описывает тело запроса /calculate
type CalculateRequest struct {
	A  float64 `json:"a"  binding:"required"`
	B  float64 `json:"b"  binding:"required"`
	Op string  `json:"op" binding:"required,oneof=add sub mul div"`
}

// CalculateResponse описывает ответ /calculate
type CalculateResponse struct {
	Result float64 `json:"result"`
	Op     string  `json:"op"`
}

// ItemResponse описывает ответ /items/:id
type ItemResponse struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// ErrorResponse описывает ошибку
type ErrorResponse struct {
	Error string `json:"error"`
}

// pingHandler godoc
// @Summary      Health check
// @Description  Returns pong
// @Tags         health
// @Produce      json
// @Success      200  {object}  PingResponse
// @Router       /ping [get]
func pingHandler(c *gin.Context) {
	c.JSON(http.StatusOK, PingResponse{Message: "pong", Status: "ok"})
}

// calculateHandler godoc
// @Summary      Calculate
// @Description  Performs add, sub, mul or div on two numbers
// @Tags         math
// @Accept       json
// @Produce      json
// @Param        request  body      CalculateRequest  true  "Input"
// @Success      200      {object}  CalculateResponse
// @Failure      400      {object}  ErrorResponse
// @Failure      422      {object}  ErrorResponse
// @Router       /calculate [post]
func calculateHandler(c *gin.Context) {
	var req CalculateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
		return
	}

	var result float64
	switch req.Op {
	case "add":
		result = req.A + req.B
	case "sub":
		result = req.A - req.B
	case "mul":
		result = req.A * req.B
	case "div":
		if req.B == 0 {
			c.JSON(http.StatusUnprocessableEntity, ErrorResponse{Error: "division by zero"})
			return
		}
		result = req.A / req.B
	}

	c.JSON(http.StatusOK, CalculateResponse{Result: result, Op: req.Op})
}

// getItemHandler godoc
// @Summary      Get item by ID
// @Description  Returns item by integer ID
// @Tags         items
// @Produce      json
// @Param        id   path      int  true  "Item ID"
// @Success      200  {object}  ItemResponse
// @Failure      400  {object}  ErrorResponse
// @Failure      404  {object}  ErrorResponse
// @Router       /items/{id} [get]
func getItemHandler(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Error: "id must be an integer"})
		return
	}
	if id <= 0 {
		c.JSON(http.StatusNotFound, ErrorResponse{Error: "item not found"})
		return
	}
	c.JSON(http.StatusOK, ItemResponse{ID: id, Name: "Item " + idStr})
}