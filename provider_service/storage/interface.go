package storage

import (
	"context"
	"io"
)

type ObjectStorage interface {
	Upload(ctx context.Context, key string, data io.Reader) error
}
