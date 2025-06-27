package storage

import (
	"context"
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// SelfhostedStorage uploads to Ceph (S3-compatible), typically deployed in a Kubernetes cluster.
type SelfhostedStorage struct {
	uploader *s3manager.Uploader
	bucket   string
}

// NewSelfhostedStorage creates a new storage instance that targets an in-cluster Ceph gateway.
func NewSelfhostedStorage(endpoint, region, accessKey, secretKey, bucket string) (*SelfhostedStorage, error) {
	sess, err := session.NewSession(&aws.Config{
		Region:           aws.String(region),
		Endpoint:         aws.String(endpoint),
		Credentials:      credentials.NewStaticCredentials(accessKey, secretKey, ""),
		S3ForcePathStyle: aws.Bool(true), // Required for Ceph RGW
	})
	if err != nil {
		return nil, err
	}

	return &SelfhostedStorage{
		uploader: s3manager.NewUploader(sess),
		bucket:   bucket,
	}, nil
}

// Upload streams a file to the configured Ceph bucket.
func (s *SelfhostedStorage) Upload(ctx context.Context, key string, data io.Reader) error {
	_, err := s.uploader.UploadWithContext(ctx, &s3manager.UploadInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
		Body:   data,
	})
	return err
}
