package com.bloodbank.controller;
import com.bloodbank.entity.User;
import com.bloodbank.repository.UserRepository;
import com.bloodbank.security.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.Set;

@RestController @RequestMapping("/api/auth")
public class AuthController {
    @Autowired UserRepository repo;
    @Autowired JwtUtil jwt;
    @Autowired PasswordEncoder enc;

    // Roles a person may choose when signing up. SUPER_ADMIN is never self-assigned.
    private static final Set<String> SIGNUP_ROLES = Set.of("DONOR", "CAMP_COORDINATOR", "HOSPITAL_ADMIN");

    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody Map<String,String> b) {
        String username = b.get("username"), email = b.get("email"), password = b.get("password");
        String role = b.getOrDefault("role", "DONOR");
        if (username == null || username.isBlank() || email == null || !email.contains("@")
                || password == null || password.length() < 8)
            return ResponseEntity.badRequest().body(Map.of("error",
                "Username, a valid email and a password of at least 8 characters are required"));
        if (!SIGNUP_ROLES.contains(role))
            return ResponseEntity.badRequest().body(Map.of("error","This role cannot be chosen at signup"));
        if (repo.existsByUsername(b.get("username")))
            return ResponseEntity.badRequest().body(Map.of("error","Username already taken"));
        if (repo.existsByEmail(b.get("email")))
            return ResponseEntity.badRequest().body(Map.of("error","Email already registered"));
        User u = User.builder()
            .username(b.get("username")).email(b.get("email"))
            .password(enc.encode(b.get("password")))
            .role(role).build();
        repo.save(u);
        return ResponseEntity.ok(Map.of("message","Account created! Please login."));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String,String> b) {
        var opt = repo.findByUsername(b.get("username"));
        // One message for both cases, so the answer never reveals which usernames exist
        if (opt.isEmpty() || b.get("password") == null || !enc.matches(b.get("password"), opt.get().getPassword()))
            return ResponseEntity.status(401).body(Map.of("error","Invalid username or password"));
        User u = opt.get();
        return ResponseEntity.ok(Map.of(
            "token", jwt.generate(u.getUsername(), u.getRole()),
            "role",  u.getRole(),
            "username", u.getUsername(),
            "userId", u.getId(),
            "email", u.getEmail()
        ));
    }
}
