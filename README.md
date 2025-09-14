# JWT and Cookie Security in FastAPI

This document explains the security considerations for JWT and cookies, and how to handle expired or invalid tokens in a FastAPI application.

## 1. Security Considerations for Cookies and JWT

1. **HttpOnly Cookie**

   * Cookies with `HttpOnly=True` cannot be accessed by JavaScript.
   * Protects against **XSS (Cross-Site Scripting)** attacks since malicious scripts cannot read the token.

2. **Secure Cookie**

   * Cookies are sent only over **HTTPS**.
   * Ensures tokens are transmitted securely and prevents interception over insecure networks.

3. **SameSite Cookie**

   * `SameSite=Lax` or `SameSite=Strict` prevents **CSRF (Cross-Site Request Forgery)** attacks.
   * The browser will not send cookies automatically in cross-site requests.

4. **Short-lived Access Token + Long-lived Refresh Token**

   * Access Token: short-lived (e.g., 15 minutes).
   * Refresh Token: long-lived (e.g., 7 days) used to obtain new Access Tokens.
   * Reduces risk if an Access Token is stolen.

5. **Secure JWT Signing**

   * Use a strong algorithm (e.g., `HS256` or `RS256`).
   * Use a long, random `SECRET_KEY` to prevent brute-force attacks.

6. **Avoid storing tokens in localStorage**

   * Tokens in localStorage are accessible by JavaScript and vulnerable to XSS.
   * Prefer HttpOnly cookies instead.

## 2. Handling Expired or Invalid Tokens

1. **Expired Token**

   * If a JWT has expired, return **HTTP 401 Unauthorized**.
   * Message: `"Token expired, please login again"`.
   * The user can use a Refresh Token or login again to get a new Access Token.

2. **Invalid Token**

   * If the JWT signature is invalid or token is malformed, return **HTTP 401 Unauthorized**.
   * Message: `"Invalid token"`.

3. **Wrong Token Type**

   * Ensure that only Refresh Tokens are used for refreshing Access Tokens.
   * Sending an Access Token instead of a Refresh Token should return **HTTP 401 Unauthorized**.

4. **Missing Token**

   * If no token is provided in the request, return **HTTP 401 Unauthorized**.
   * Message: `"Token missing"`.

## Summary

* HttpOnly and Secure cookies protect against XSS and CSRF.
* Access/Refresh token combination balances security and usability.
* Proper handling of token errors prevents unauthorized access and provides clear feedback to the user.
