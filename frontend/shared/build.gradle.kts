plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
}

val hasAndroidSdk = providers.gradleProperty("includeAndroid").orNull == "true" ||
    providers.environmentVariable("ANDROID_HOME").isPresent ||
    providers.environmentVariable("ANDROID_SDK_ROOT").isPresent ||
    rootProject.file("local.properties").exists()

if (hasAndroidSdk) {
    apply(plugin = "com.android.kotlin.multiplatform.library")
    apply(from = "android-target.gradle")
}

kotlin {
    jvm("desktop")
    jvmToolchain(21)

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.materialIconsExtended)
            implementation(compose.ui)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.client.logging)
            implementation(libs.ktor.client.websockets)
            implementation(libs.ktor.serialization.kotlinx.json)
            implementation(libs.voyager.navigator)
            implementation(libs.voyager.tab.navigator)
        }
        named("desktopMain") {
            dependencies {
                implementation(libs.ktor.client.cio)
            }
        }
    }
}
