import React, { useState } from "react";
import { useForm } from "react-hook-form";

export default function DistrictAdminForm() {
  const [step, setStep] = useState(1);
  const [otp, setOtp] = useState("");
  const [sentOtp, setSentOtp] = useState("");
  const [emailForOtp, setEmailForOtp] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm({ mode: "onChange" });

  const {
    register: registerOtp,
    handleSubmit: handleOtpSubmit,
    formState: { errors: otpErrors },
  } = useForm({ mode: "onChange" });

  const onFormSubmit = (data) => {
    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    setOtp(generatedOtp);
    setEmailForOtp(data.email);
    setSentOtp(`OTP sent to ${data.email}`);
    setStep(2);
    console.log("Generated OTP:", generatedOtp);
  };

  const onOtpSubmit = (data) => {
    if (data.otp === otp) {
      alert("✅ OTP Verified Successfully!");
      reset();
      setStep(1);
    } else {
      alert("❌ Incorrect OTP. Please try again.");
    }
  };

  const resendOtp = () => {
    const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
    setOtp(generatedOtp);
    setSentOtp(`New OTP sent to ${emailForOtp}`);
    console.log("Resent OTP:", generatedOtp);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/district.jpeg')] bg-cover bg-center bg-fixed p-6">
      <div className="bg-white/10 backdrop-blur-2xl rounded-2xl border border-white/30 shadow-2xl p-8 w-full max-w-md transition-all duration-300">
        <h1 className="text-2xl font-bold text-white text-center mb-6">
          District Administrator
        </h1>

        {/* STEP 1 → FORM */}
        {step === 1 && (
          <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-white font-medium mb-1">Email:</label>
              <input
                type="email"
                {...register("email", {
                  required: "Email is required",
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "Enter a valid email address",
                  },
                })}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none ${
                  errors.email
                    ? "border-red-500 focus:border-red-500"
                    : "border-white/30 focus:border-green-400"
                } bg-white/20 text-white placeholder-gray-300`}
                placeholder="admin@example.com"
              />
              {errors.email && (
                <p className="text-red-400 text-sm mt-1">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-white font-medium mb-1">
                Password:
              </label>
              <input
                type="password"
                {...register("password", {
                  required: "Password is required",
                  minLength: {
                    value: 6,
                    message: "Password must be at least 6 characters",
                  },
                })}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none ${
                  errors.password
                    ? "border-red-500 focus:border-red-500"
                    : "border-white/30 focus:border-green-400"
                } bg-white/20 text-white placeholder-gray-300`}
                placeholder="Enter password"
              />
              {errors.password && (
                <p className="text-red-400 text-sm mt-1">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* District Name */}
            <div>
              <label className="block text-white font-medium mb-1">
                District Name:
              </label>
              <input
                type="text"
                {...register("districtName", {
                  required: "District name is required",
                  minLength: {
                    value: 3,
                    message: "District name must be at least 3 characters",
                  },
                })}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none ${
                  errors.districtName
                    ? "border-red-500 focus:border-red-500"
                    : "border-white/30 focus:border-green-400"
                } bg-white/20 text-white placeholder-gray-300`}
                placeholder="Enter district name"
              />
              {errors.districtName && (
                <p className="text-red-400 text-sm mt-1">
                  {errors.districtName.message}
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={!isValid}
              className={`w-full py-2 rounded-lg text-white font-semibold transition-all duration-300 ${
                isValid
                  ? "bg-green-600 hover:bg-green-700 shadow-lg"
                  : "bg-gray-400 cursor-not-allowed"
              }`}
            >
              Next
            </button>
          </form>
        )}

        {/* STEP 2 → OTP */}
        {step === 2 && (
          <form
            onSubmit={handleOtpSubmit(onOtpSubmit)}
            className="space-y-5 mt-2"
          >
            <p className="text-green-300 text-sm text-center">{sentOtp}</p>

            {/* OTP */}
            <div>
              <label className="block text-white font-medium mb-1">OTP:</label>
              <input
                type="text"
                {...registerOtp("otp", {
                  required: "OTP is required",
                  pattern: {
                    value: /^[0-9]{6}$/,
                    message: "OTP must be 6 digits",
                  },
                })}
                className={`w-full px-3 py-2 rounded-lg border focus:outline-none ${
                  otpErrors.otp
                    ? "border-red-500 focus:border-red-500"
                    : "border-white/30 focus:border-green-400"
                } bg-white/20 text-white placeholder-gray-300`}
                placeholder="Enter 6-digit OTP"
              />
              {otpErrors.otp && (
                <p className="text-red-400 text-sm mt-1">
                  {otpErrors.otp.message}
                </p>
              )}
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                type="submit"
                className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-semibold transition-all duration-300"
              >
                Verify OTP
              </button>
              <button
                type="button"
                onClick={resendOtp}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-all duration-300"
              >
                Resend OTP
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
