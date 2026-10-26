package com.bloodbank.config;
import com.bloodbank.security.JwtFilter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.*;
import java.util.List;

@Configuration @EnableWebSecurity
public class SecurityConfig {
    @Autowired JwtFilter jwtFilter;
    @Value("${cors.allowed-origins}") private String allowedOrigins;

    @Bean
    public SecurityFilterChain chain(HttpSecurity http) throws Exception {
        http
            .cors(c -> c.configurationSource(cors()))
            .csrf(c -> c.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("SUPER_ADMIN")
                .requestMatchers("/api/coordinator/**")
                    .hasAnyRole("CAMP_COORDINATOR","SUPER_ADMIN")
                .requestMatchers("/api/hospital/**")
                    .hasAnyRole("HOSPITAL_ADMIN","SUPER_ADMIN")
                // FIXED: All roles can access donor endpoints (for dashboard data)
                .requestMatchers("/api/donor/**")
                    .hasAnyRole("DONOR","SUPER_ADMIN","HOSPITAL_ADMIN","CAMP_COORDINATOR")
                .requestMatchers("/api/ml/**")
                    .hasAnyRole("DONOR","SUPER_ADMIN","HOSPITAL_ADMIN","CAMP_COORDINATOR")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean public PasswordEncoder encoder() { return new BCryptPasswordEncoder(); }

    @Bean
    public CorsConfigurationSource cors() {
        var cfg = new CorsConfiguration();
        cfg.setAllowedOrigins(List.of(allowedOrigins.split(",")));
        cfg.setAllowedMethods(List.of("GET","POST","PUT","DELETE","OPTIONS","PATCH"));
        cfg.setAllowedHeaders(List.of("Authorization","Content-Type"));
        cfg.setAllowCredentials(true);
        var src = new UrlBasedCorsConfigurationSource();
        src.registerCorsConfiguration("/**", cfg);
        return src;
    }
}
