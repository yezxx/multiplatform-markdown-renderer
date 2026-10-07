import json, os, shutil, urllib.request, urllib.parse

VER = "0.45.0"
FORK = "/home/yezi/main/src/kotlin-markdown-renderer"
OUT = os.path.join(FORK, "gh-pages-repo")
CENTRAL = "https://repo1.maven.org/maven2/"

LIGHT_VARIANT_ATTRS = {
    "org.gradle.category": "library",
    "org.gradle.jvm.environment": "non-jvm",
    "org.gradle.usage": "kotlin-api",
    "org.jetbrains.kotlin.native.target": "linux_x64",
    "org.jetbrains.kotlin.platform.type": "native",
}
MODULES = {
    "multiplatform-markdown-renderer": {
        "klib": "multiplatform-markdown-renderer/build/libs/multiplatform-markdown-renderer-linuxX64Main-0.45.0.klib",
        "deps": [
            ("org.jetbrains", "markdown", "0.7.9"),
            ("org.jetbrains.kotlinx", "kotlinx-coroutines-core", "1.11.0"),
            ("org.jetbrains.kotlinx", "kotlinx-collections-immutable", "0.5.2"),
        ],
    },
    "multiplatform-markdown-renderer-m3": {
        "klib": "multiplatform-markdown-renderer-m3/build/libs/multiplatform-markdown-renderer-m3-linuxX64Main-0.45.0.klib",
        "deps": [
            ("com.mikepenz", "multiplatform-markdown-renderer", VER),
            ("org.jetbrains", "markdown", "0.7.9"),
        ],
    },
    "multiplatform-markdown-renderer-code": {
        "klib": "multiplatform-markdown-renderer-code/build/libs/multiplatform-markdown-renderer-code-linuxX64Main-0.45.0.klib",
        "deps": [
            ("com.mikepenz", "multiplatform-markdown-renderer", VER),
            ("dev.snipme", "highlights", "1.1.0"),
        ],
    },
}

for module, spec in MODULES.items():
    base = f"{CENTRAL}com/mikepenz/{module}/{VER}/"
    gmm = json.load(urllib.request.urlopen(f"{base}{module}-{VER}.module"))
    # 上游变体的 available-at 是相对路径：改成绝对 URL，否则从这个仓库解析时会 404
    for v in gmm["variants"]:
        at = v.get("available-at")
        if at:
            at["url"] = urllib.parse.urljoin(base, at["url"])
    klib_name = f"{module}-linuxX64Main-{VER}.klib"
    gmm["variants"].append({
        "name": "linuxX64ApiElements-published",
        "attributes": LIGHT_VARIANT_ATTRS,
        "dependencies": [{"group": g, "module": m, "version": {"requires": v}} for g, m, v in spec["deps"]],
        "files": [{"name": klib_name, "url": klib_name}],
    })
    dst = os.path.join(OUT, "com", "mikepenz", module, VER)
    os.makedirs(dst, exist_ok=True)
    json.dump(gmm, open(os.path.join(dst, f"{module}-{VER}.module"), "w"), indent=2)
    shutil.copy(os.path.join(FORK, spec["klib"]), os.path.join(dst, klib_name))
    pom = urllib.request.urlopen(f"{base}{module}-{VER}.pom").read()
    open(os.path.join(dst, f"{module}-{VER}.pom"), "wb").write(pom)
    print("wrote", module, "->", dst)

print("\n仓库根目录:", OUT)
