package main

import (
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	_ "lab10/go-service/docs" // автогенерированная swag-документация
)

func setupRouter() *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(loggingMiddleware())

	// Swagger UI — задание 8
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	r.GET("/ping", pingHandler)
	r.POST("/calculate", calculateHandler)
	r.GET("/items/:id", getItemHandler)

	return r
}