package main

import (
	"log"
	"os"

	"provider_service/storage" // Replace with your actual module path
)

func setupStorage() storage.ObjectStorage {
	backend := os.Getenv("STORAGE_BACKEND")
	switch backend {

	case "s3":
		s3, err := storage.NewS3Storage(
			os.Getenv("S3_ENDPOINT"),
			os.Getenv("S3_REGION"),
			os.Getenv("S3_ACCESS_KEY"),
			os.Getenv("S3_SECRET_KEY"),
			os.Getenv("S3_BUCKET"),
		)
		if err != nil {
			log.Fatalf("Failed to initialize S3 storage: %v", err)
		}
		return s3

	case "selfhosted":
		selfhosted, err := storage.NewSelfhostedStorage(
			os.Getenv("CEPH_ENDPOINT"),
			os.Getenv("CEPH_REGION"),
			os.Getenv("CEPH_ACCESS_KEY"),
			os.Getenv("CEPH_SECRET_KEY"),
			os.Getenv("CEPH_BUCKET"),
		)
		if err != nil {
			log.Fatalf("Failed to initialize selfhosted storage: %v", err)
		}
		return selfhosted

	default:
		log.Fatalf("Unsupported STORAGE_BACKEND: %s", backend)
		return nil
	}
}
