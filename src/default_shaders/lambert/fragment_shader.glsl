#version 410 core

struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
};

in vec2 fragmentTexCoord;
in vec3 fragmentNormal;
in vec3 fragmentPosition;
in vec3 fragAtmosphereColor;
in float fragAtmosphereIntensity;

uniform sampler2D imageTexture;
uniform PointLight Lights[8];
uniform vec3 cameraPosition;

out vec4 color;
vec3 calculatePointLight(PointLight light, vec3 fragPosition, vec3 fragNormal);


void main()
{
    //ambient
    vec3 temp = 0.5 * texture(imageTexture, fragmentTexCoord).rgb;

    for (int i = 0; i < 8; i++) {
        temp += calculatePointLight(Lights[i], fragmentPosition, fragmentNormal);
    }

    color = vec4(temp, 1);
}

vec3 calculatePointLight(PointLight light, vec3 fragPosition, vec3 fragNormal) {

    vec3 baseTexture = texture(imageTexture, fragmentTexCoord).rgb;
    vec3 result = vec3(0);

    //geometric data
    vec3 fragLight = light.position - fragPosition;
    float distance = length(fragLight);
    fragLight = normalize(fragLight);
    vec3 fragCamera = normalize(cameraPosition - fragPosition);
    vec3 halfVec = normalize(fragLight + fragCamera);

    //diffuse
    result += light.color * light.intensity * max(0.0, dot(fragNormal, fragLight)) / (distance * distance) * baseTexture;

    //specular
    result += light.color * light.intensity * pow(max(0.0, dot(fragNormal, halfVec)),12) / (distance * distance);

    return result;
}
