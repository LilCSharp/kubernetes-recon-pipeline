package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	store := setupStorage()

	router := gin.Default()
	router.POST("/upload", func(c *gin.Context) {
		fileHeader, err := c.FormFile("file")
		if err != nil {
			c.String(http.StatusBadRequest, err.Error())
			return
		}
		file, _ := fileHeader.Open()
		defer file.Close()

		err = store.Upload(c.Request.Context(), fileHeader.Filename, file)
		if err != nil {
			c.String(http.StatusInternalServerError, err.Error())
			return
		}

		c.String(http.StatusOK, "Upload successful")
	})

	router.Run(":8080")
}
