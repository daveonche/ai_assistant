# Elgg Developer Guide: File System

Delta distillation of <https://learn.elgg.org/en/stable/guides/file-system.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/file-system.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Filestore location

- The filestore lives in the site's `dataroot`, configured during installation
  and modifiable via site settings in the Admin interface.

## Directory structure

- The structure is tied to file ownership by Elgg entities: when the first file
  owned by an entity is written, a directory for the entity GUID is created
  inside a parent bucket directory (buckets are bound to 5000 GUIDs). Files
  owned by user GUID 7777 live under `5000/7777/`.
- Filenames may embed subdirectory names (the `$prefix` seen throughout the
  code); e.g. that user's avatars sit under `5000/7777/profile/`.

## Writing files

- Write with an `ElggFile` instance. `ElggFile` extends `ElggObject` and can be
  stored as a real entity, but that is not always necessary (e.g. when writing
  image thumbs):

```php
$file = new ElggFile();
$file->owner_guid = 7777;
$file->setFilename('portfolio/files/sample.txt');
$file->open('write');
$file->write('Contents of the file');
$file->close();

// to upgrade this file to an entity
$file->save();
```

## Reading files

```php
// from an Elgg entity
$file = get_entity($guid);
readfile($file->getFilenameOnFilestore());
```

```php
// arbitrary file on the filestore
$file = new ElggFile();
$file->owner_guid = 7777;
$file->setFilename('portfolio/files/sample.txt');

// option 1
$file->open('read');
$contents = $file->grabFile();
$file->close();

// option 2
$contents = file_get_contents($file->getFilenameOnFilestore());
```

## Serving files

- Serve filestore files with `elgg_get_inline_url()` and
  `elgg_get_download_url()`. Both accept three arguments:

| Argument | Meaning |
| :--- | :--- |
| `file` | the `ElggFile` instance to serve |
| `use_cookie` | when `true`, URL validity is limited to the current session |
| `expires` | expiration time of the URL |

- Treat `use_cookie` and `expires` as access-control levers. Avatars typically
  get a long expiration and no session restriction, so browsers can cache the
  image; the file service then sends `Not Modified` headers on consecutive
  requests.
- The default `use_cookie` behaviour is controlled on the admin security
  settings page.
- For entities under Elgg's access control, keep cookies enabled so access
  settings are respected and users cannot share download URLs.
- Invalidate all previously generated URLs by updating the file's modified
  time, e.g. with `touch()`.

## Embedding files

- Inline and download URLs are volatile (bound to the user session and the
  file's modification time) and are not suitable for embedding — embed URLs
  must be permanent. Use `elgg_get_embed_url()` to embed an entity icon.

## Handling file uploads

- Single upload — form:

```php
echo elgg_view('input/file', [
    'name' => 'upload',
    'label' => 'Select an image to upload',
    'help' => 'Only jpeg, gif and png images are supported',
]);
```

- Single upload — action:

```php
$uploaded_file = elgg_get_uploaded_file('upload');
if (!$uploaded_file) {
    return elgg_error_response("No file was uploaded");
}

$supported_mimes = [
    'image/jpeg',
    'image/png',
    'image/gif',
];

$mime_type = elgg()->mimetype->getMimeType($uploaded_file->getPathname());
if (!in_array($mime_type, $supported_mimes)) {
    return elgg_error_response("{$mime_type} is not supported");
}

$file = new ElggFile();
$file->owner_guid = elgg_get_logged_in_user_guid();
if ($file->acceptUploadedFile($uploaded_file)) {
    $file->save();
}
```

- Multiple uploads: set `'name' => 'upload[]'` and `'multiple' => true` on the
  input, then iterate `elgg_get_uploaded_files('upload')` in the action with
  the same per-file body as above.
- Uploaded images get an automatic attempt to fix their orientation.

## Temporary files

- `elgg_get_temp_file()` returns an `ElggTempFile`: it has all the file
  functions of `ElggFile` but writes to the system temp folder.
- Gotcha: `ElggTempFile` cannot be saved to the database — attempting it throws
  `Elgg\Exceptions\Filesystem\IOException`.
