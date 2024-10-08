// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    id("org.sonarqube") version "5.1.0.4882"
}

sonar {
    properties {
        property("sonar.projectKey", "AndroLMS")
        property("sonar.organization", "lesaint")
        property("sonar.host.url", "https://sonarcloud.io")
        property("sonar.sourceEncoding", "UTF-8")
    }
}

// add a dependency of sonar task onto any task lint of any subproject
// use afterEvaluate otherwise the task set is empty
val sonarTask = tasks.getByName("sonar")
subprojects {
    afterEvaluate {
        project.tasks.filter { it.name == "lint" }.forEach{ sonarTask.dependsOn(it)}
    }
}
