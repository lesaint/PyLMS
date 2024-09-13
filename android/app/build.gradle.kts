import java.io.FileNotFoundException

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "fr.javatronic.lms.android"
    compileSdk = 34

    defaultConfig {
        applicationId = "fr.javatronic.lms.android"
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
        // source: https://stackoverflow.com/a/28250257
        setProperty("archivesBaseName", "AndroLMS-$versionName")
    }
    signingConfigs {
        register("release") {
            keyAlias = "release"
            storePassword = System.getenv("SIGNING_STORE_PASSWORD")
            keyPassword = System.getenv("SIGNING_KEY_PASSWORD")
            // inspiration: https://proandroiddev.com/how-to-securely-build-and-sign-your-android-app-with-github-actions-ad5323452ce
            val runnerTemp = System.getenv("RUNNER_TEMP")
            if (runnerTemp == null) {
                storeFile = file("signing_keystore.jks")
            } else {
                // Gradle executing within a Github Action
                // Keystore is expected to be created from a Github repository secret as a temporary
                // file in the Runner's temp directory
                // keystore and key password are expected to be provided as Environment variables
                // and both are mandatory
                val keystoreDir = File(runnerTemp, "androlms")
                val keystoreFile = File(keystoreDir, "signing_keystore.jks")

                if (!keystoreDir.exists()) {
                    throw FileNotFoundException("${keystoreDir.absolutePath} not found")
                }
                if (!keystoreFile.exists()) {
                    throw FileNotFoundException("${keystoreFile.absolutePath} not found")
                }
                storeFile = keystoreFile
            }
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
