import React, { useState } from "react";
import { useForm } from "react-hook-form";

function VoterReg() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm({ mode: "onChange" });

  const [photoPreview, setPhotoPreview] = useState(null);

  const onSubmit = (data) => {
    console.log("Form Submitted:", data);
    alert("Form submitted successfully!");
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 1024 * 1024) {
        alert("File size must be less than 1MB");
        e.target.value = null;
        return;
      }
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cover bg-center bg-fixed bg-[url('/thumb.jpeg')] p-6">
      <div className="relative bg-white/10 backdrop-blur-2xl rounded-2xl border border-white/20 shadow-2xl w-full max-w-xl p-8 transition-all duration-500 hover:scale-[1.02]">
        {/* Liquid Glow Border Effect */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-green-300 via-purple-400 to-pink-400 opacity-30 blur-xl -z-10"></div>

        <h1 className="text-3xl font-bold text-center text-white drop-shadow-lg mb-6">
          Voter Registration
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Name */}
          <div>
            <label className="block text-white/90 font-medium mb-1">Name:</label>
            <input
              type="text"
              {...register("name", {
                required: "Name is required",
                minLength: { value: 3, message: "At least 3 characters" },
              })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white placeholder-gray-300 border focus:outline-none ${
                errors.name
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
              placeholder="Enter your full name"
            />
            {errors.name && (
              <p className="text-red-300 text-sm mt-1">{errors.name.message}</p>
            )}
          </div>

          {/* Father's Name */}
          <div>
            <label className="block text-white/90 font-medium mb-1">
              Father's Name:
            </label>
            <input
              type="text"
              {...register("fatherName", {
                required: "Father's name is required",
              })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white placeholder-gray-300 border focus:outline-none ${
                errors.fatherName
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
              placeholder="Enter father's name"
            />
            {errors.fatherName && (
              <p className="text-red-300 text-sm mt-1">
                {errors.fatherName.message}
              </p>
            )}
          </div>

          {/* Gender */}
          <div>
            <label className="block text-white/90 font-medium mb-1">Gender:</label>
            <select
              {...register("gender", { required: "Please select your gender" })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white border focus:outline-none ${
                errors.gender
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
            >
              <option value="">Select Gender</option>
              <option value="Male" className="text-black">Male</option>
              <option value="Female" className="text-black">Female</option>
              <option value="Transgender" className="text-black">Transgender</option>
            </select>
            {errors.gender && (
              <p className="text-red-300 text-sm mt-1">{errors.gender.message}</p>
            )}
          </div>

          {/* DOB */}
          <div>
            <label className="block text-white/90 font-medium mb-1">Date of Birth:</label>
            <input
              type="date"
              {...register("dob", {
                required: "Date of Birth is required",
                validate: (value) => {
                  const today = new Date();
                  const dob = new Date(value);
                  const age = today.getFullYear() - dob.getFullYear();
                  return age >= 18 || "You must be at least 18 years old";
                },
              })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white border focus:outline-none ${
                errors.dob
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
            />
            {errors.dob && (
              <p className="text-red-300 text-sm mt-1">{errors.dob.message}</p>
            )}
          </div>

          {/* Address */}
          <div>
            <label className="block text-white/90 font-medium mb-1">Home Address:</label>
            <textarea
              {...register("address", { required: "Address is required" })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white border focus:outline-none resize-none h-20 ${
                errors.address
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
              placeholder="Enter your address"
            ></textarea>
            {errors.address && (
              <p className="text-red-300 text-sm mt-1">{errors.address.message}</p>
            )}
          </div>

          {/* EPIC ID */}
          <div>
            <label className="block text-white/90 font-medium mb-1">EPIC ID:</label>
            <input
              type="text"
              {...register("epicId", {
                required: "EPIC ID is required",
                pattern: {
                  value: /^[A-Z]{3}\d{7}$/,
                  message: "Format: ABC1234567 (3 letters + 7 digits)",
                },
              })}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white placeholder-gray-300 border focus:outline-none ${
                errors.epicId
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
              placeholder="ABC1234567"
            />
            {errors.epicId && (
              <p className="text-red-300 text-sm mt-1">{errors.epicId.message}</p>
            )}
          </div>

          {/* Photo Upload */}
          <div>
            <label className="block text-white/90 font-medium mb-1">Upload Photo:</label>
            <input
              type="file"
              accept="image/*"
              {...register("photo", {
                required: "Photo is required",
                validate: {
                  lessThan1MB: (files) =>
                    files[0]?.size < 1024 * 1024 || "File size must be less than 1MB",
                },
              })}
              onChange={handlePhotoChange}
              className={`w-full rounded-lg px-3 py-2 bg-white/20 text-white border cursor-pointer focus:outline-none ${
                errors.photo
                  ? "border-red-400 focus:border-red-400"
                  : "border-white/30 focus:border-green-400"
              }`}
            />
            {photoPreview && (
              <img
                src={photoPreview}
                alt="Preview"
                className="mt-3 w-full rounded-lg border border-white/40"
              />
            )}
            {errors.photo && (
              <p className="text-red-300 text-sm mt-1">{errors.photo.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!isValid}
            className={`w-full py-3 rounded-xl text-white font-semibold shadow-lg transition-all duration-300 ${
              isValid
                ? "bg-green-500 hover:bg-green-600 hover:shadow-green-500/50"
                : "bg-gray-500 cursor-not-allowed"
            }`}
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}

export default VoterReg;
