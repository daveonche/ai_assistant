# Dependency File Templates

Use the appropriate template for the selected core technology. All versions must be exact, with no ranges or prefixes.

## Concrete Working Example: Python

If the project uses Python, create `requirements.txt` with a realistic, directly usable example:

```
Flask==3.0.3
SQLAlchemy==2.0.31
python-dotenv==1.0.1
```

Use actual versions after compatibility verification. The example above is a concrete starting point, not a placeholder.

## Template Gallery

### Node.js / JavaScript / TypeScript

```json
{
  "name": "[project-name]",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "[package-name]": "[exact-version]",
    "[package-name]": "[exact-version]"
  }
}
```

### Deno Fresh

```
{
  "imports": {
    "$fresh/": "https://deno.land/x/fresh@<exact-version>/",
    "preact": "https://esm.sh/preact@<exact-version>",
    "preact/": "https://esm.sh/preact@<exact-version>/",
    "preact-render-to-string": "https://esm.sh/*preact-render-to-string@<exact-version>",
    "@preact/signals": "https://esm.sh/*@preact/signals@<exact-version>",
    "@preact/signals-core": "https://esm.sh/*@preact/signals-core@<exact-version>",
    "zod": "https://esm.sh/zod@<exact-version>"
  }
}
```

Note: Do not include tasks, permissions, or compilerOptions in the dependency file.

### Java / Maven

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>[group-id]</groupId>
    <artifactId>[artifact-id]</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <dependency>
            <groupId>[group-id]</groupId>
            <artifactId>[artifact-id]</artifactId>
            <version>[exact-version]</version>
        </dependency>
    </dependencies>
</project>
```

### .NET

```xml
<Project Sdk="Microsoft.NET.SDK">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  
  <ItemGroup>
    <PackageReference Include="[package-name]" Version="[exact-version]" />
    <PackageReference Include="[package-name]" Version="[exact-version]" />
  </ItemGroup>
</Project>
```

## Validation Reminder

After generating, ensure:

- Exact version strings only.
- No range operators (`^`, `~`, `>=`, etc.).
- No prefix characters.
- Only runtime dependencies.
