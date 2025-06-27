package storage

import (
	"context"
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

type S3Storage struct {
	uploader *s3manager.Uploader
	bucket   string
}

func NewS3Storage(endpoint, region, accessKey, secretKey, bucket string) (*S3Storage, error) {
	sess, err := session.NewSession(&aws.Config{
		Region:           aws.String(region),
		Endpoint:         aws.String(endpoint),
		Credentials:      credentials.NewStaticCredentials(accessKey, secretKey, ""),
		S3ForcePathStyle: aws.Bool(true),
	})
	if err != nil {
		return nil, err
	}

	return &S3Storage{
		uploader: s3manager.NewUploader(sess),
		bucket:   bucket,
	}, nil
}

func (s *S3Storage) Upload(ctx context.Context, key string, data io.Reader) error {
	_, err := s.uploader.UploadWithContext(ctx, &s3manager.UploadInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
		Body:   data,
	})
	return err
}
