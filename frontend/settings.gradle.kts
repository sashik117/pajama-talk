pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "PajamaTalk"

fun hasAndroidSdk(): Boolean {
    val localProperties = file("local.properties")
    if (localProperties.exists() && localProperties.readText().contains("sdk.dir")) return true
    return System.getenv("ANDROID_HOME") != null || System.getenv("ANDROID_SDK_ROOT") != null
}

val includeAndroid = providers.gradleProperty("includeAndroid").orNull == "true" || hasAndroidSdk()

include(":shared")
include(":desktopApp")

if (includeAndroid) {
    include(":androidApp")
}
